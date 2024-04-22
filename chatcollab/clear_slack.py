from slack_cleaner2 import *
import os

slack_token = os.environ['SLACK_API_TOKEN']
s = SlackCleaner(slack_token)

def delete_all_messages_files_in_channel():
    for msg in s.msgs(filter(match('chatcollab'), s.conversations)):
        msg.delete(replies=True, files=True)
