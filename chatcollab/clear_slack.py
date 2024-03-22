from slack_cleaner2 import *
import os

slack_token = os.environ['SLACK_API_TOKEN']
s = SlackCleaner(slack_token)

def delete_all_messages_files_in_channel():
    # list of users
    s.users
    # list of all kind of channels
    s.conversations

    # delete all messages in -bots channels
    for msg in s.msgs(filter(match('personality-experiment'), s.conversations)): # Hard coded, TODO change
    # delete messages, its files, and all its replies (thread)
        msg.delete(replies=True, files=True)

    # delete all general messages and also iterate over all replies
    for msg in s.c.general.msgs(with_replies=True):
        msg.delete()