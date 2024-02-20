import os
from slack_sdk import WebClient
from datetime import datetime
import time

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
)

def post_slack_message(channel, username, text):
    response = client.chat_postMessage(channel=channel, username=username, text=text)
    print(response)

def get_channel_history(channel, count=100):
    try:
        # Call the conversations.history method using the WebClient
        result = client.conversations_history(channel=channel, limit=count)
        messages = result.get('messages', []) if result['ok'] else []
        return messages
    except Exception as e:
        print(f"Error retrieving channel history: {e}")
        return []

# See if last message was from the bot
def last_message_from_bot(channel):
    messages = get_channel_history(channel)
    if messages:
        last_message = messages[0]
        if last_message['username'] == "Peter Williams (AI)":
            return True
        else:
            return False
    else:
        return False

def style_channel_history(channel_history):
    # Style history
    styled_history = []
    timestamps = []
    for message in channel_history:
        try:
            styled_history.append(f"{message['username']}: {message['text']}")
        except KeyError:
            # Get username from user ID
            user_info = client.users_info(user=message['user'])
            username = user_info['user']['real_name']
            styled_history.append(f"{username}: {message['text']}")

        timestamps.append(message['ts'])
    
    # Style timestamps as readable
    for i in range(len(timestamps)):
        timestamps[i] = datetime.fromtimestamp(float(timestamps[i])).strftime('%Y-%m-%d %H:%M:%S')
    for i in range(len(styled_history)):
        styled_history[i] = f"{styled_history[i]}\n"
    return styled_history

def get_formatted_channel_history(channel):
    result = style_channel_history(get_channel_history(channel))
    if result:
        result.reverse()
        return result
    else:
        return []
