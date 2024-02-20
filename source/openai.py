# Utility functions for ChatGPT

#------- [IMPORT LIBRARIES] -------#
import requests
import os


#------- [ENV VARIABLES] -------#
openai_gpt_key = os.environ['OPENAI_GPT_KEY']


#------- [FUNCTIONS] -------#
def ask_chatgpt(query):
    """Ask ChatGPT using Openai
    Inputs:
        query: String query to input to chatgpt4
    Returns:
        response.json(): Json form of response from API
    """
 
    return ask_gpt_4(query, temperature=0.3)

def ask_gpt_3(query, temperature=0.1):
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
