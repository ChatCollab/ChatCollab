# Utility functions for ChatGPT

#------- [IMPORT LIBRARIES] -------#
import requests
import os


#------- [ENV VARIABLES] -------#
openai_gpt_key = os.environ['OPENAI_GPT_KEY']

#------- [VARIABLES] -------#
globals()["weak_total_rate_limit"] = 1200 # This is weak because it does not use a persistent database to track usage.
globals()["rate_limit_usage"] = 0

#------- [FUNCTIONS] -------#

def check_rate_limit():
    """Check the rate limit for the API
    Returns:
        bool: True if rate limit is not reached, False if rate limit is reached
    """
    if globals()["rate_limit_usage"] > globals()["weak_total_rate_limit"]:
        raise Exception("Rate limit reached")
    else:
        globals()["rate_limit_usage"] += 1
        print("\n\nNumber of requests made: ", globals()["rate_limit_usage"],"\n\n")
        return False


def ask_chatgpt(query):
    """Ask ChatGPT using Openai
    Inputs:
        query: String query to input to chatgpt4
    Returns:
        response.json(): Json form of response from API
    """
    if check_rate_limit():
        return "Rate limit reached. Try again later."

    return ask_gpt_4(query, temperature=0.3)

def ask_gpt_3(query, temperature=0.1):

    if check_rate_limit():
        return "Rate limit reached. Try again later."
    
    # Ask ChatGPT3 using openai
    
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_gpt_key}'
    }

    data = {
        "model": "gpt-3.5-turbo-1106",  # Model to use
        "messages": [{"role": "user", "content": query}],
        "temperature": temperature,
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]['content']

def ask_gpt_4(query, temperature=0.2):

    if check_rate_limit():
        return "Rate limit reached. Try again later."

    # Ask ChatGPT using openai
    
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_gpt_key}'
    }

    data = {
        "model": "gpt-4",  # Model to use
        "messages": [{"role": "user", "content": query}],
        "temperature": temperature,
        "max_tokens": 2000,
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]['content']
