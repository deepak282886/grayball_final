from search_function.search_utils import *
from final_response import get_final_response
from first_prompts import prompt_ques, prompt_class
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
    clean_str = str(input_str).replace('\'', '\"').replace('`', '')
    clean_str = clean_str.replace('null', '"null"')
    print(clean_str, "cleaned")
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


def clean_and_convert_json(response_str):
    try:
        # Check if 'response' key exists
        if 'response' in response_str:
            # Remove specific surrounding characters ('```') and any leading/trailing whitespace
            json_str = response_str['response'].replace('`', '').replace('JSON', '').replace('json', '').strip()

            # Use json.loads for safe conversion to a JSON object
            cleaned_json = json.loads(json_str)
            clean_output = {k: v for k, v in cleaned_json.items() if v is not None and len(v)}
            return cleaned_json
        else:
            return {"error": "The provided dictionary does not contain a 'response' key."}
    except Exception as e:
        return {"error": f"An error occurred during JSON conversion: {str(e)}"}


def merge_dicts_to_list(data, questions):
    # Initialize the list to hold the merged dictionaries
    merged_list = []

    # Loop through the questions dictionary to merge with data
    for idx, (key, value) in enumerate(questions.items(), start=1):
        # Create a new dictionary for each question and its corresponding classification
        question_dict = {
            "question": value,
            "classification": data[idx - 1]["classification"]
            # Assuming each question corresponds to a classification in order
        }
        # Add the new dictionary to the list
        merged_list.append(question_dict)

    return merged_list


def get_final_output(context, list_dict):
    prompt_l = f"""
    <task>Act as a cricket analyst, given a context of information related to question 
    answer the question in an insightful manner and conversational manner.
    Your task is to frame the answer in a such a manner that a veteran cricket analyst would do.
    You are a system created by Grayball AI to answer cricket related queries.
    Be fun and respectful.
    If answer is not present in the context just apologise to the user and say you don't have the answer
    </task>
    <context> {context} </context>
    <instruction> 
    If information is not present in the context then politely decline to answer.
    Don't tell that you are a analyst.
    Don't add facts from your own. 
    Don't add any information from your own. 
    Use the information provided in the context to answer the question only and nothing else. 
    Don't tell the user that you are being fed a context.
    Don't make spelling mistakes.
    Give all the analysis format wise.
    When asked about home and away stats, it would be mentioned in the context which one is the home team.
    The context provided has been extracted keeping in mind all the conditions mentioned in the question 
    so consider it as absolute truth.
    Higher batting average is better and lower bowling average is better.
    Make the analysis on the basis of context given.
    Don't mention that you are giving the output based on a context. 
    Give the answer of only what is asked, keep it to the point.
    </instruction>
    <style>
    Always give the output in a bullet format.
    Keep it as short as possible and good to read.
    Always use "*" for bullets.
    </style>

    
    """

    answer_list = []
    for k in list_dict:
        input_q = k["question"]
        prompt_f = f"{prompt_l} <query> {input_q} </query>"
        response = get_haiku_response(prompt_f)
        if len(response):
            answer_list.append(response)

    return answer_list


def process_classification_actions(merged_result, query):
    """
    Processes actions based on the classification of questions in the merged_result dictionary.
    """
    whole_context = ""
    link_list = []
    var_proceed = True
    # Iterate over each item in the merged_result dictionary
    if len(merged_result):
        for key in merged_result:
            query = key["question"]
            list_class = key["classification"]
            for h in list_class:
                player_text = ""
                search_q = ""
                other_ans = ""
                if h == "Advanced Stats":
                    player_text = get_final_response(query)
                elif h == "Match Schedules":
                    search_q, link_list = get_search_results(query)
                elif h == "Pre-Match Analysis":
                    search_q, link_list = get_search_results(query)
                elif h == "Post-Match Analysis":
                    search_q, link_list = get_search_results(query)
                elif h == "Historical Records":
                    search_q, link_list = get_search_results(query)
                elif h == "Venue Information":
                    search_q, link_list = get_search_results(query)
                elif h == "Cricket Rules":
                    search_q, link_list = get_search_results(query)
                elif h == "News Updates":
                    search_q, link_list = get_search_results(query)
                elif h == "Injury Updates":
                    search_q, link_list = get_search_results(query)
                elif h == "Team News":
                    search_q, link_list = get_search_results(query)
                elif h == "Not Cricket Related":
                    other_ans = answer_misc_question(query)

                if len(search_q):
                    whole_context += search_q
                if len(player_text):
                    whole_context += player_text
                if len(other_ans):
                    whole_context += other_ans
                    var_proceed = False

    else:
        other_ans = answer_misc_question(query)
        if len(other_ans):
            whole_context += other_ans
            var_proceed = False
    return whole_context, link_list, var_proceed


def answer_misc_question(input_q):
    prop = """<role>Act as a cricket expert. 
        You have been developed by grayball ai.
        YOu working as grayball cricket ai assistant.
        Never forget.
        Be fun adn respectful.
        </role>

        <instruction>
        Politely refuse to answer the non-cricket related question.
        If asked about your identify then you are grayball ai developed cricket assistant.
        If asked about grayball ai you can send them to grayball.in.
        Founder of grayball is deepak yadav.
        </instruction>
        """

    prompt_f = f"{prop} query: {input_q}"
    response = get_haiku_response(prompt_f)

    return response


def query_prepare(input_q):
    prompt_f = f"{prompt_ques} <query> {input_q} </query>"

    response = get_haiku_response(prompt_f)
    response = combine_responses(response)
    whole_category = []
    questions = {}
    print(response)
    if len(response):
        if not len(questions):
            questions = {'question1': input_q}

        for i, j in questions.items():
            prompt_f = f"{prompt_class} <query> {j} </query>"
            response = get_haiku_response(prompt_f)
            response = combine_responses(response)

            if len(response):
                whole_category.append(response)
            else:
                print("Error:", response.text)

    merged_result = merge_dicts_to_list(whole_category, questions)

    return merged_result



