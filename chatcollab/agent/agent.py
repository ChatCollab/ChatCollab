from agent.timeline_interface import get_timeline_events, post_timeline_event, get_institutional_knowledge
from source.slack_functions import get_formatted_channel_history
import time
import random
from datetime import datetime, timedelta
import json
from source.openai import ask_chatgpt, ask_gpt_4
import os

slack_channel_id = os.environ['SLACK_CHANNEL_ID']

globals()["last_prompt_with_no_as_response"] = {}

def get_allowed_agents():
    filename = 'allowed_threads.json'

    # Reading the list back from the JSON file
    with open(filename, 'r') as f:
        allowed_agents = json.load(f)

    print(f"List loaded from {filename}: {allowed_agents}")
    return allowed_agents


def get_n_min_before_now(n):
    current_time = datetime.now()

    # Time n minutes behind the current time
    time_behind = current_time - timedelta(minutes=n)

    # Format the timestamp
    timestamp = time_behind.strftime("%Y-%m-%dT%H:%M:%S.%f")

    return timestamp


def check_if_any_agent_typing(my_agent_name):
    # Check if any agent is typing, return string with agent names if so
    events = get_timeline_events(start=get_n_min_before_now(2))

    # Track the latest typing status for each agent
    agent_typing_status = {}
    for event in events:
        if 'Typing Indicator' in event['title']:
            for tag in event['tags']:
                if tag.startswith('from:'):
                    agent_name = tag.split(':', 1)[1]
                    agent_typing_status[agent_name] = (event['title'] == 'Typing Indicator Start')

    # Get list of agents who are currently typing
    agents_typing = [agent for agent, is_typing in agent_typing_status.items() if is_typing]

    # Filter myself out of the list (edge case)
    agents_typing = [agent for agent in agents_typing if agent!=my_agent_name]

    # Return a string with agent names
    if len(agents_typing)>1:
        return True, "\n\nNote you should very likely wait for the following users that are typing on Slack: " + ", ".join(agents_typing)
    elif len(agents_typing)==1:
        return True, "\n\nNote you should very likely wait for the following user that is typing on Slack: " + ", ".join(agents_typing)
    else:
        return False, ""

def replace_newlines_in_strings(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = value.replace("\\n", "\n")
    return obj

def get_prompt_with_instructions(agent_name, description_of_role, persona, slack_channel, instructions):
    chat_history = get_formatted_channel_history(slack_channel_id)

    # Add chat history
    prompt = "<Chat History>\nThe following is the chat history on Slack:\n\n"

    for message in chat_history:
        prompt += message + "\n"
    
    if len(chat_history)==0:
        prompt += "No messages in the Slack channel. Feel free to send a messafe introducing yourself!\n\n"
    else:
        prompt += "\n\n(The above message was the last one sent in the Slack channel)</Chat History>\n\n"

    # Add persona
    prompt += f"<Persona>You are {agent_name} in the above conversation.\n\n{persona}.\n\n</Persona>\n\n"

    # Final instructions
    prompt += instructions

    return prompt

def create_run_autonomous_agent(agent_name, description_of_role, persona, slack_channel, print_to_output, random_id):
    globals()["last_prompt_with_no_as_response"][agent_name] = ""

    start_time = time.time()
    timeout_amt_of_time = 60*60*3 # 3 hours

    timeout_val = 0
    while timeout_val<10 and random_id in get_allowed_agents() and time.time()-start_time<timeout_amt_of_time:
        talked = False
        if True:
        # try:
            choice_result, context = choose_action(agent_name=agent_name, description_of_role=description_of_role, persona=persona, slack_channel=slack_channel, print_to_output=print_to_output)
            
            if choice_result==1 or choice_result==2:
                post_timeline_event(title="Typing Indicator Start", payload=f"...", tags=[f"from:{agent_name}", "type:event"])
                print_to_output("Typing...")
                talked = True

                # Get events
                full_events_list = get_timeline_events()

                if choice_result==1:
                    send_message(agent_name, description_of_role, persona, slack_channel, print_to_output, full_events_list, context)

                elif choice_result==2:
                    generate_file(agent_name, description_of_role, persona, slack_channel, print_to_output, full_events_list, context)
        # except Exception as e:
        #     print(e)
        #     print("[CRITICAL] Error in agent, restarting in 3 seconds...")
        #     time.sleep(1) #Note its 3 when you add the 2 at startup
        #     timeout_val+=1
        #     continue

        if talked:
            # End "..." signal
            post_timeline_event(title="Typing Indicator End", payload=f"...", tags=[f"from:{agent_name}", "type:event"])

        # Sleep to allow space for humans to respond, and reduce API usage
        # time.sleep(2)
        # Sleep random amount of time between 1-3 seconds
        time.sleep(random.randint(1,15)) #2,2 for no variation, 1,15 for variation
    
    if random_id not in get_allowed_agents():
        print_to_output("[TERMINATED] Agent has been stopped as thread is closed. This means another browser has the admin app open, and since only one agent system can run at a time in the same slack, this session has been stopped.\n\n **Please reload this page to restart**\n\n")
        print("[TERMINATED] Agent has been stopped as thread is closed. This means another browser has the admin app open, and since only one agent system can run at a time in the same slack, this session has been stopped.\n\n **Please reload this page to restart**\n\n")
        return
    
    if time.time()-start_time>=timeout_amt_of_time:
        print_to_output("[TERMINATED] Agent has been stopped as it has been running for 3 hours. This is to prevent accidental use of resources.\n\n **Please reload this page to restart**\n\n")
        print("[TERMINATED] Agent has been stopped as it has been running for 3 hours.\n\n **Please reload this page to restart**\n\n")
        return
    
    print_to_output("[TERMINATED] Agent has been stopped due to 10 critical errors total.\n\n **Please reload this page to restart**\n\n")
    print("[TERMINATED] Agent has been stopped due to 10 critical errors total.\n\n **Please reload this page to restart**\n\n")
    return


# Do you want to:
# [Option 1] Draft and send a message
# [Option 2] Generate a file you promised to create
# [Option 3] Do nothing and wait for another agent to speak


# @v3.2
def choose_action(agent_name, description_of_role, persona, slack_channel, print_to_output):

    if get_formatted_channel_history(slack_channel_id)==globals()["last_prompt_with_no_as_response"][agent_name]:
        print("Already considered as no (option 3). Waiting for new messages.")
        print_to_output("Already considered as no (option 3). Waiting for new messages.\n")
        return 3, None

    instructions = f"""<Instructions>You are an AI teammate, {agent_name}, on Slack. As you are autonomous, you must decide if you want to take an action. As an AI, you CAN create any files including code. You have the transcript above, emulate human behavior. Do not hallucinate updating or sending something if you do not see the content in the history: Nothing exists outside the provided transcript.

You have the following options. Please choose one by responding with \"Option 1\", \"Option 2\", or \"Option 3\". Do not repeat yourself, if you have already responded and others are not waiting for your work, it is not time to respond. Provide your brief reasoning first, then your choice.
    
Do you want to:
[Option 1] Draft and send a message
[Option 2] Generate a file you promised to create or are responsible for creating
[Option 3] Do nothing and wait for another agent to speak

</Instructions>
    
<Examples>
Option 1
Reason: As the product manager, since the CEO has asked me to create the PRD, it is time for me to acknowledge his message.
    
Option 2: 
Reason: My next step is to start working on the code. I have promised to create the code, so I should generate it now. As an AI, Option 2 is how I can generate code.

Option 3:
Reason: The last message in the conversation was sent by me. There are no new messages or questions directed towards me that require a response.
</Examples>

Response (provide explaination first then the option):"""
    
    prompt = get_prompt_with_instructions(agent_name, description_of_role, persona, slack_channel, instructions)

    anyone_typing, typing_message = check_if_any_agent_typing(agent_name)

    if anyone_typing: # If anyone typing, add that note to the prompt
        prompt += typing_message

    print("---- PROMPT [Lvl A.1]----")
    print(prompt)
    response = ask_chatgpt(prompt)
    print("---- RESPONSE ----")
    print(response)
    print_to_output(response + "\n"+"""\nDo you want to:
[Option 1] Draft and send a message
[Option 2] Generate a file you promised to create or are responsible for creating
[Option 3] Do nothing and wait for another agent to speak\n""")

    if "Option 1" in response:
        print("Time to talk...")
        # print_to_output("Time to talk...")
        return 1, response

    elif "Option 2" in response:
        print("Time to generate file(s)...")
        # print_to_output("Time to generate file(s)...")
        return 2, response

    elif "Option 3" in response:
        print("Not time to talk")
        # print_to_output("Not time to talk")

        if anyone_typing==False: # In other words, did agent possibly decide not to talk when no one else is typing? If so, skip. Otherwise, store the last prompt.
            globals()["last_prompt_with_no_as_response"][agent_name] = get_formatted_channel_history(slack_channel_id)

        return 3, None
    else:
        print("\n\n[Warning]: Invalid response\n\n")
        return 3, None


# @v3.2
def send_message(agent_name, description_of_role, persona, slack_channel, print_to_output, full_events_list, context):

    knowledge = get_institutional_knowledge(full_events_list)

    instructions = f"""<Background>{knowledge}</Background><Internal Thoughts>{context}</Internal Thoughts>\n\n<Instructions>Provide your response for the slack conversation as {agent_name}. Be relevant to the conversation. Be very CONCISE, and you are an AI, you cannot meet.\n\nProvide your response structured as follows:
{{"message": "This is my message as {agent_name}."}}
</Instructions>"""
    
    prompt = get_prompt_with_instructions(agent_name, description_of_role, persona, slack_channel, instructions)

    print("---- PROMPT [Lvl B.1]----")
    print(prompt)

    # Fixes newline between lines in JSON which would cause parsing error
    response = ask_gpt_4(prompt).replace("\",\n\"","\",\"").replace("\n","\\n")
    print("---- RESPONSE ----")
    print(response)

    print_to_output("Response: "+response + "\n\n")

    # Parse JSON
    try:
        response = json.loads(response)
    except Exception as e:
        print(e)
        print_to_output("[WARNING] Invalid JSON response, try again") # If happens, replace prompt for json with just output of the plain message.
        raise Exception("Invalid JSON response, try again")
    
    response = replace_newlines_in_strings(response)

    # Send message
    post_timeline_event(title="Slack Message", payload=response['message'], tags=["to:slack", f"from:{agent_name}", "type:action", "action:send_message"])
    return


# @v3.2
def generate_file(agent_name, description_of_role, persona, slack_channel, print_to_output, full_events_list, context):

    # First create prompt
    knowledge = get_institutional_knowledge(full_events_list)
    
    instructions = f"""<Background>{knowledge}</Background><Internal Thoughts>{context}</Internal Thoughts>\n\n<Instructions>You are {agent_name}. If there is a file generation you have promised to complete which you have not done yet, but should do now, add the action title and the prompt to the JSON below. Be aware, you can ONLY create and send files, no other actions are possible. The prompt field is for constructing a direct prompt for a LLM to generate file(s) relevant to the action. In the prompt, include ALL context relevant from the provided Slack conversation.
\n\nProvide your response structured as follows:
{{"title": "This is the title of the next relevant file generation action I should take as {agent_name}. If there is no action for YOUR SPECIFIC AGENT to take NOW (especially if you are waiting for approval or another agent's deliverable), leave this blank.","prompt":"Constructed prompt, including all the context required for the file generation task (such as a PRD or code files). If there is no action to take, leave this blank."}}
</Instructions>"""

    prompt = get_prompt_with_instructions(agent_name, description_of_role, persona, slack_channel, instructions)

    print("---- PROMPT [Lvl B.2]----")
    print(prompt)

    response = ask_gpt_4(prompt).replace("\n","\\n")
    print("---- RESPONSE ----")
    print(response)

    try:
        response = json.loads(response)
    except Exception as e:
        print(e)
        print("[WARNING] Invalid JSON response, try again")
        raise Exception("Invalid JSON response, try again")

    response = replace_newlines_in_strings(response)

    if response['title']!="":
        print("**Taking Action**")
        print_to_output("Action: "+response['title'] + "\n\n")
        task_prompt = response['title']+"\n\n"+response['prompt']
    else:
        return

    # We have task_prompt 
    prompt_for_action = task_prompt

    # Now execute prompt
    # prompt = f"""<Persona>{persona}<Persona>\n\n<Instructions>{prompt_for_action}\n\nOutput ONLY the file(s) and their names. Include ALL the required content for the content to be complete and functional: No placeholders or comments for later completion. Omit ANY commentary, just provide the file(s).</Instructions>"""
    prompt = f"""\n\n<Instructions>{prompt_for_action}\n\nOutput ONLY the file(s) and their names. Include ALL the required content for the content to be complete and functional: No placeholders or comments for later completion. Omit ANY commentary, just provide the file(s).</Instructions>"""

    print("---- PROMPT [Lvl C.1]----")
    print(prompt)

    prompt = get_prompt_with_instructions(agent_name=agent_name, description_of_role=description_of_role, persona=persona, slack_channel=slack_channel, instructions=prompt)

    response = ask_gpt_4(prompt)

    print("---- RESPONSE ----")
    print(response)

    # Send message
    post_timeline_event(title="Slack Message", payload=response, tags=["to:slack", f"from:{agent_name}", "type:action", "action:send_message"])

    return