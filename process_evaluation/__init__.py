import logging

import azure.functions as func
import azure.functions as func
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
import os
import json
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
load_dotenv()

template_1 = '''
System: You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a attribute-answer task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Relevance measures how well the answer addresses the main aspects of the attribute, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between zero to one using the following rating scale:
Zero stars : the answer is wrong or incomplete
One stars : the answer is completely correct

This rating value should always be an integer between 0 and 1. So the rating produced should be 0 or 1

Example 1:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary

Company: Tasmanian Water and Sewerage Corporation Pty Ltd

stars : 1

Example 2:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: 
ABN : 47 152 220 656

stars : 0

Example 3:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary
Billing Address : 1788 dandenong road clayton-3168

stars : 0

Example 4:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary
Billing Address : Community Housing Limited Att : Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128

stars : 1

context: {context}
{attribute}:{answer}

stars:
'''

def extract_attributes(json_data, parent_key=''):
    """
    Recursively extracts attributes and their corresponding answers from a JSON object.
    
    Args:
        json_data (dict): The JSON object to extract attributes from.

    Returns:
        list: A list of dictionaries, where each dictionary represents an attribute and its answer.
    """
    attributes_list = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_key = f"{key}" if parent_key else key
            if isinstance(value, list):
                for item in value:
                    attributes_list.extend(extract_attributes(item, new_key))
            elif isinstance(value, dict):
                attributes_list.extend(extract_attributes(value, new_key))
            else:
                attributes_list.append({new_key: value})
    return attributes_list

def evaluation(template_1, format_json_output, raw_invoice_data):
    """
    Evaluates the correctness of extracted information by comparing it with a predefined template 
    and raw invoice data using the GPT-3.5 Turbo engine.

    Parameters:
    template_1 (str): A predefined template used for generating prompts.
    format_json_output (list): A list of dictionaries containing formatted extracted information.
    raw_invoice_data (dict): Raw invoice data used as context for the evaluation.

    Returns:
    tuple: A tuple containing two lists - the first list (scoring) contains evaluation scores,
           and the second list (wrong_answers) contains extracted answers identified as incorrect.
    """

    # Define GPT-3.5 Turbo prompt templates for generating messages
    gpt3_5_prompt = PromptTemplate(
                    template=template_1,
                    input_variables=["context", "attribute", "answer"]
                )
    system_message_prompt = SystemMessagePromptTemplate(prompt=gpt3_5_prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Initialize lists to store evaluation scores and wrong answers
    scoring = []
    wrong_answers = []
    
    # Iterate through the formatted extracted information
    for dict in format_json_output:
        # Generate messages using the predefined prompts and extracted information
        for key, value in dict.items():
            messages = chat_prompt.format_prompt(context=raw_invoice_data, attribute=key, answer=value).to_messages()
            question=key
            print(question)
            chat = ChatOpenAI(engine="gpt-4-32k", temperature=0)
            
            # Generate response using GPT-3.5 Turbo
            resp = chat(messages)

            # Evaluate the response
            if resp.content == '0':
                # If the response indicates incorrect answer, store the answer and title
                wrong_answers.append({key: value})
            # Store the response content (evaluation score) in the scoring list
            scoring.append(resp.content)

    # Return the evaluation scores and wrong answers as a tuple
    return scoring, wrong_answers

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "POST":
        # Handle POST request
        try:
            req_body = req.get_json()
            json_output = req_body["json_output"]
            raw_invoice_input = req_body["raw_invoice_input"]
            attributes_list = extract_attributes(json_output)
            print(attributes_list)
            evaluation_results = evaluation(template_1,attributes_list,raw_invoice_input)
            print(evaluation_results)
            Incorrect_results = evaluation_results[1]
            relevance_scoring = sum(int(number) for number in evaluation_results[0])/len(evaluation_results[0])

            # If average is less than 1, set it to 0
            if relevance_scoring < 1:
                relevance_scoring = 0
            print(relevance_scoring)
            final_output = {
                "invoice_result" : json_output,
                "relevance_scoring" : relevance_scoring,
                "incorrect_results" : Incorrect_results
            }


            logging.info(final_output)
            print(final_output)
            return func.HttpResponse(
                json.dumps(final_output),
            #    relevance_scoring,
                mimetype="application/json",
            )

        except ValueError:
            return func.HttpResponse(
                 "Invalid request body",
                 status_code=400
            )
    
    return func.HttpResponse(
                 "Invalid request body",
                 status_code=400
            )

    

