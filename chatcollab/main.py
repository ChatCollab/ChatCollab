import streamlit as st
import threading
from chatcollab.clear_slack import delete_all_messages_files_in_channel
from chatcollab.agent.agent import *
from chatcollab.agent.timeline_interface import update_institutional_knowledge, clear_timeline

# ---- [Slack Source] ----
from chatcollab.source.source import run_slack_source

# Start async function of run_slack_source
slack_thread = threading.Thread(target=run_slack_source)

# Start the thread
slack_thread.start()
# -------------------------


st.header("Autonomous Agent Collaboration Engine (AACE)")
st.caption("Enabling autonomous AI agents to collaborate with humans via Slack.")

if 'is_first_run' not in st.session_state:
    print("Cleared timeline for new run!")
    clear_timeline()
    st.session_state.is_first_run = False

# Initialize session state variables
if 'name' not in st.session_state:
    st.session_state['name'] = ""
if 'role' not in st.session_state:
    st.session_state['role'] = ""
if 'description' not in st.session_state:
    st.session_state['description'] = ""
if 'knowledge' not in st.session_state:
    st.session_state['knowledge'] = "In our software team, the CEO coordinates the timeline for each project. The product manager and developers do not start work until it has been approved by the CEO. Once that occurs, the product manager first creates and shares a PRD with the team. Development does not start until this PRD is approved by the CEO. Then, the software with test cases is developed. It is important for all code to have strong documentation through inline comments."


if 'is_deleting' not in st.session_state:
    st.session_state.is_deleting = False

# Function to wrap delete operation
def delete_messages():
    st.session_state.is_deleting = True
    delete_all_messages_files_in_channel()
    st.session_state.is_deleting = False

# Add Clean Slack Button
if st.button("Clean Slack - Clear AI Messages", disabled=st.session_state.is_deleting):
    delete_messages()

# Institutional Knowledge
knowledge = st.text_area("Institutional Knowledge", value=st.session_state['knowledge'], height=150)

if st.button("Update Institutional Knowledge"):
    update_institutional_knowledge(knowledge)

# add space
st.markdown("---")

# Callback functions to autofill
def autofill_peter():
    st.session_state['name'] = "Peter (CEO)"
    st.session_state['role'] = "CEO"
    st.session_state['description'] = "You are the CEO of a development firm that creates software for a client, who will provide their requirements, and can answer clarifying questions. Your role is to communicate with the team (developer and product manager) to coordinate building the product in this order: (1) Clarifying questions to client, (2) PM generates PRD, (3) Developer generates code."


def autofill_boshen():
    st.session_state['name'] = "Boshen (Product Manager)"
    st.session_state['role'] = "Product Manager"
    st.session_state['description'] = "You are a professional product manager. Your role is to design a concise, usable, efficient product. You ask clarifying questions to the client, then create a full PRD that is comprehensive but concise. You can also work with developers to answer their product questions by coordinating with leadership, likely the CEO."


def autofill_isabelle():
    st.session_state['name'] = "Isabelle (Developer)"
    st.session_state['role'] = "Developer"
    st.session_state['description'] = "You are a professional developer. Your role is to build modular and easy to read and maintain code. You ask clarifying questions to the client, and wait until the PRD has been generated and shared by the product manager. Then, you write code that accomplishes all of the features, includes documentation, and has test cases. You will write code to Slack."

# Section to Create AI Agents
st.subheader("Create AI Agents")

# Buttons for predefined agents
if st.button("Fill Boshen (Product Manager)"):
    autofill_boshen()

if st.button("Fill Isabelle (Developer)"):
    autofill_isabelle()

if st.button("Fill Peter (CEO)"):
    autofill_peter()


if 'agents' not in st.session_state:
    st.session_state.agents = []

# Check flags and set default values for text inputs
default_name = ""
default_role = ""
default_description = ""
if st.session_state.get('fill_peter'):
    default_name = "Peter (CEO)"
    default_role = "CEO"
    default_description = "You are the CEO of a new startup that creates tic-tac-toe python games with code. Your role is to communicate with the team to coordinate building the product to your specifications."
    st.session_state['fill_peter'] = False

if st.session_state.get('fill_boshen'):
    default_name = "Boshen (Product Manager)"
    default_role = "Product Manager"
    default_description = "You are a professional product manager. Your role is to design a concise, usable, efficient product. You create PRDs and work with developers to answer their product questions by coordinating with leadership. Work with the full team to accomplish the task at hand."
    st.session_state['fill_boshen'] = False

if st.session_state.get('fill_isabelle'):
    default_name = "Isabelle (Developer)"
    default_role = "Developer"
    default_description = "You are a professional developer. Your role is to build PEP8 compliant, elegant, modular, easy to read and maintain code. You write code and work with the product manager to build the product at hand, asking clarifying questions along the way when needed. Work with the team to accomplish the task at hand. You will write code to Slack."
    st.session_state['fill_isabelle'] = False


def parent_create_run_autonomous_agent(name, role, description, channel_id, output):
    # Add everything from print to output
    def print_to_output(message):
        #add message to top of output
        output.insert(0, message)
        print(message)

    create_run_autonomous_agent(name, role, description, channel_id, print_to_output)
    pass

# Limit to 5 agents
if len(st.session_state.agents) < 5:
    with st.form("agent_creation_form"):        
        name = st.text_input("Agent Name (Put Role in Parentheses)", value=st.session_state['name'])
        role = st.text_input("Role", value=st.session_state['role'])
        description = st.text_area("Description", value=st.session_state['description'], height=100)
        channel_id = "C05QHBA5066"
        create_agent = st.form_submit_button("Create Agent")

        if create_agent and name and role and description and channel_id:
            output = []
            agent_thread = threading.Thread(target=parent_create_run_autonomous_agent, args=(name, role, description, channel_id, output))
            agent_thread.start()
            st.session_state.agents.append({"name": name, "role": role, "output": output})

st.markdown("---")

# Display Running AI Agents and their outputs
st.subheader("Running AI Agents")

index_count = 0
for agent in st.session_state.agents:
    st.write(f"Name: {agent['name']}, Role: {agent['role']}")
    # Output for each agent
    if 'output' in agent:
        unique_key = index_count
        index_count+=1
        st.text_area(f"Output for {agent['name']}", key=unique_key, value="\n".join(agent['output']), height=200, disabled=True)


# Rerun every 1 second to update the outputs
time.sleep(1)
st.experimental_rerun()