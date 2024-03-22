from agent.timeline_interface import *
from source.slack_functions import post_slack_message
import time
import os

slack_channel_id = os.environ['SLACK_CHANNEL_ID']

public_key = "placeholder"
private_key = "placeholder"

SHORT_list_of_viewed_events = []
SHORT_list_of_executed_events = [] # Only used for diagnostic purposes


def run_slack_source(print_to_output):
    while True:
        slack_events = filter_events_by_tag("to:slack", get_timeline_events(start=get_timestamp_x_minutes_ago(3)))

        for event in slack_events:
            print(event)
            if (str(event['id'])+str(event['created_at'])) not in SHORT_list_of_viewed_events:
                print(f"New event! ID {event['id']}")
                print_to_output(f"New event! ID {event['id']}")
                SHORT_list_of_viewed_events.append(str(event['id'])+str(event['created_at']))

                # Check if "type:action" is a tag
                if "type:action" in event['tags']:
                    print("Action found!")
                    print("Executing action...")
                    print_to_output("Executing action...")

                    # Execute the action
                    # Check if "action:send_slack_message" is a tag
                    if "action:send_message" in event['tags']:
                        print("Sending Slack message...")
                        print_to_output("Sending Slack message...")

                        #Find username from tag with from:* (e.g. from:Peter Williams (AI))
                        username = [tag for tag in event['tags'] if "from:" in tag][0].split(":")[1].strip()

                        time.sleep(1)
                        post_slack_message(channel=slack_channel_id, username=username, text=event['payload'])
                        
                        post_timeline_event(title="Slack Message Sent", payload=event['payload'], tags=["to:slack", "from:Peter Williams (AI)", "type:receipt"],new_private_key=private_key, new_public_key=public_key)
                        
                        SHORT_list_of_executed_events.append(str(event['id'])+str(event['created_at']))
                        print("Done!")
                        print_to_output("Done!")
                        print(SHORT_list_of_executed_events)
                    else:
                        SHORT_list_of_executed_events.append(str(event['id'])+str(event['created_at']))
                        pass
            else:
                pass

        time.sleep(1)
        print("Checking...", time.time())
        print_to_output("Checking... "+ str(time.time()))
