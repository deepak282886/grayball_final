import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

import boto3
import json


def get_haiku_response(prompt):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id='AKIATROVE4AWEMIHPN46',
        aws_secret_access_key='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')

    # Variables for Bedrock API
    modelId = "anthropic.claude-3-haiku-20240307-v1:0"
    contentType = 'application/json'
    accept = 'application/json'

    # Messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    # Body
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": messages
    })

    # Run Bedrock API
    response = bedrock.invoke_model(
        modelId=modelId,
        contentType=contentType,
        accept=accept,
        body=body
    )

    # Print response
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

def clean_null_values(data):
    """
    Recursively remove dictionary keys with None or 'null' values.

    Parameters:
    data (dict or list): The input data which can be a dictionary or a list.

    Returns:
    dict or list: The cleaned data without None or 'null' values.
    """
    if isinstance(data, dict):
        return {
            key: clean_null_values(value)
            for key, value in data.items()
            if value is not None and str(value) != 'null'
        }
    elif isinstance(data, list):
        return [clean_null_values(item) for item in data if item is not None and item != 'null']
    else:
        return data

def clean_and_parse_json(input_str):
    """
    Clean the input string by removing any non-JSON characters and parse it as JSON.
    """
    # Remove unnecessary characters that might interfere with JSON parsing
    #     print("start", input_str)
    clean_str = str(input_str).replace('\'', '\"').replace('`', '')
    clean_str = clean_str.replace('null', '"null"')
    clean_str = clean_str.replace('not specified', '')

    clean_str = clean_str.replace('`', '').replace('JSON', '').replace('json', '').strip()
    clean_json = eval(clean_str)
    clean_json = clean_null_values(clean_json)
    #     print("end", clean_json)
    try:
        return clean_json
    except json.JSONDecodeError:
        # Return an empty dictionary if parsing fails
        return {}


def combine_responses(*args):
    """
    Combine multiple JSON string responses into a single dictionary, excluding keys with null values.
    """
    combined_dict = {}
    for arg in args:
        # Parse each argument string into a dictionary
        parsed_dict = clean_and_parse_json(arg)
        #         print("parse", parsed_dict)
        # Iterate through the dictionary items
        for key, value in parsed_dict.items():
            # Exclude null keys and merge dictionaries
            if value is not None and str(value) != "null":
                combined_dict[key] = value
    return combined_dict

def internet_search(query):
    """Searches the internet using DuckDuckGo."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        return results if results else "No results found."
from datetime import date


def get_search_results(query):
    today = date.today()
    query += f"date {str(today)}"
    results = internet_search(query)
    preresponse = ""

    link_list = []
    for k in range(len(results)):
        print(results[k]['href'], "pl")
        try:
            full_jj = results[k]['href']
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
            webpage = requests.get(full_jj, headers= headers)
            soup = BeautifulSoup(webpage.content, "html.parser")
            text_t = soup.get_text()
            prop = f"""<context> {text_t} </context>
            <question> {query} </question>
            <task>
            The context contains article from news website. Your task is to summarize it and send it in the format
            where first would be date then summary. 
            The question asked is also given customize the summary accordingly.
            </task>
            """

            response = get_haiku_response(prop)
            # print(response, "news")
            # response = combine_responses(response)
            preresponse += response #.json()["response"]
            link_list.append(full_jj)
            print(link_list, "here")
        except:
            pass
        
    return preresponse, link_list