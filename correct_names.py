import sqlite3
import pandas as pd
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np
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

prompt = """<role>
You are a spell checker with determines which name the user meant from their input.
Given a input name and a list of probable names it matches. 
You have to choose the name which it matches the best. 
</role>
<task>
Your task is to go through the list of names and 
analyse and find out which name the user meant to type. 
Don;t write code for it just interpret it from your understanding.
</task>

<example>

<input>
ro sharma
<probable_list> ['Amar Sharma', 'Amar Sharma', 'Om Sharma', 'Karan Sharma', 'Tushar Sharma', 'Manan Sharma', 'Naman Sharma', 'Mani Sharma', 'Anil Sharma', 'Rajan Sharma', 'Ishant Sharma', 'Kamal Sharma', 'Rohit Sharma', 'Vishal Sharma', 'Ashish Sharma', 'Ajay Sharma', 'Bharat Sharma', 'Rahul Sharma', 'Rahul Sharma', 'Mohit Sharma']</probable_list> 

<answer> ["Rohit Sharma"] </answer>
</example>

<instruction>

Just give put the name in a list nothing else. 
Sometimes exact match would also be given then choose that. 
Sometimes extremely bad spelling would be given then you can return empty list. 
Your role is to pick the best match from the list. 
Don't give any explanation.
</instruction>
"""


def get_model_name(prompt, misspelled_word, correction_candidates):
    prompt_final = f"{prompt} <input> {misspelled_word} </input> <probable_list> {correction_candidates} </probable_list> <answer>"
    model_name = get_haiku_response(prompt_final)
    return model_name


def get_correct_name(misspelled_word, model_name):
    # Vectorize the misspelled word
    if isinstance(misspelled_word, list):
        misspelled_word = misspelled_word[0]

    neigh = load(f'/home/deepak/grayball_final/name_models/{model_name}.joblib')
    vocabulary = np.load(f'/home/deepak/grayball_final/name_lists/{model_name}.npy', allow_pickle=True)
    vectorizer = load(f'/home/deepak/grayball_final/name_models/{model_name}_vect.joblib')

    vec_misspelled = vectorizer.transform([misspelled_word])

    # Find the nearest neighbors (i.e., the most similar words in the vocabulary)
    nearest_neighbor_indices = neigh.kneighbors(vec_misspelled, return_distance=False)

    name_list = [vocabulary[idx] for idx in nearest_neighbor_indices[0]]

    model_name = get_model_name(prompt, misspelled_word, name_list)

    start = model_name.find('[') + 1
    end = model_name.find(']')

    # Extracting the name
    extracted_name = model_name[start + 1:end - 1]

    return extracted_name

def modify_names(query_dict):

    for key, value in query_dict.items():
        if key == "league":
            event_name = get_correct_name(value, "event_name")
            if event_name:
                query_dict[key] = event_name

        if key == "venue":
            venue_name = get_correct_name(value, "venue")
            if venue_name:
                query_dict[key] = venue_name

        if key == "city":
            city_name = get_correct_name(value, "city")
            if city_name:
                query_dict[key] = city_name

    return query_dict






