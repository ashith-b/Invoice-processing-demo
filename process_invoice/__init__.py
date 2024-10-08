import logging

import azure.functions as func

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
import json
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

template = '''
System: As your AI assistant, my purpose is to assist you in extracting information from invoices and provide the details in JSON format. Here's how it works:

Example 1:
input_invoice: {input}
output_json : {output}


input : {input_invoice}
output:
'''

def invoice_processing(json_schema, input_text):
    """
    Extracts structured information from the input text using a given JSON schema.

    Parameters:
    json_schema (dict): JSON schema describing the expected structure of the input data.
    input_text (str): Input text containing unstructured information to be processed.

    Returns:
    str: Extracted information formatted according to the JSON schema.
    """

    # Define a prompt to instruct the algorithm about its task
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a world-class algorithm for extracting information in structured formats."),
            ("human", "Use the given format to extract information from the following input: {input_text}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ]
    )

    # Initialize the language model (OpenAI GPT-3.5 Turbo) for conversation
    llm = ChatOpenAI(engine="gpt-4-32k", temperature=0)

    # Create a structured output processing chain
    chain = create_structured_output_chain(json_schema, llm, prompt, verbose=True)

    # Process the input text and extract structured information
    output = chain.run(input_text)

    # Return the extracted structured information
    return output


def invoice_processing_gpt_4(json_schema,input_text):
    """
    Extracts structured information from the input text using a given JSON schema.

    Parameters:
    json_schema (dict): JSON schema describing the expected structure of the input data.
    input_text (str): Input text containing unstructured information to be processed.

    Returns:
    str: Extracted information formatted according to the JSON schema.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a world class algorithm for extracting information in structured formats."),
            ("human", "Use the given format to extract information from the following input: {input_text}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ]
    )
    # Initialize the language model (OpenAI GPT-4) for conversation
    llm = ChatOpenAI(engine="gpt-4-32k",temperature=0)
    # Create a structured output processing chain
    chain = create_structured_output_chain(json_schema , llm, prompt, verbose=True)
    # Process the input text and extract structured information
    output = chain.run(input_text)
    # Return the extracted structured information
    return output

def process_multiple_schemas(input_text, json_schema_1, json_schema_2):
    """
    Extracts structured information from the input text using two different JSON schemas.

    Parameters:
    input_text (str): Input text containing unstructured information to be processed.
    json_schema_1 (dict): First JSON schema describing the expected structure of the input data.
    json_schema_2 (dict): Second JSON schema describing an alternative structure of the input data.

    Returns:
    list: A list containing the extracted structured information based on both schemas.
    """

    # Initialize an empty list to store the results from different schemas
    results = []
    
    # Process input using the first schema and append the result to the list
    result_1 = invoice_processing(json_schema_1, input_text)
    results.append(result_1)
    
    # Process input using the second schema and append the result to the list
    result_2 = invoice_processing(json_schema_2, input_text)
    results.append(result_2)
    
    # Return the list of extracted structured information based on both schemas
    return results


# def format_json_output(schema, data):
    # """
    # Formats the given data based on the provided JSON schema.

    # Parameters:
    # schema (dict): JSON schema describing the expected structure of the data.
    # data (dict): Data to be formatted based on the schema.

    # Returns:
    # list: A list of dictionaries containing formatted data with titles, descriptions, and corresponding answers.
    # """

    # # Initialize an empty list to store the formatted output
    # result = []

    # # Iterate through the properties defined in the schema
    # for key, value in schema["properties"].items():
    #     # Check if the property is an array
    #     if value["type"] == "array":
    #         # Get the nested data for the array property
    #         nested_data = data.get(key, [])
    #         # Get the schema for items in the array
    #         nested_schema = value["items"]
    #         # Process each item in the array recursively
    #         for item in nested_data:
    #             nested_result = format_json_output(nested_schema, item)
    #             result.extend(nested_result)
    #     else:
    #         # Extract title, description, and answer for non-array properties
    #         title = value.get("title")
    #         description = value.get("description")
    #         answer = data.get(key, "Not Provided")
    #         # Store the formatted data in a dictionary and append to the result list
    #         result.append({'title': title, 'description': description, 'answer': answer})

    # # Return the formatted output as a list of dictionaries
    # return result




def generate_invoice_response(template, invoice_example, processed_json, input_invoice):
    """
    Generates a chat response using the specified template and input data.

    Parameters:
    template (str): Template for formatting the chat prompt.
    invoice_example (str): Input invoice example data.
    processed_json (str): Processed JSON data.
    input_invoice (str): Input invoice information.

    Returns:
    str: Chat response generated by GPT-4 model.
    """
    gpt4_prompt = PromptTemplate(
        template=template,
        input_variables=["input", "output", "input_invoice"]
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt=gpt4_prompt)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Format the chat prompt using the provided input data
    messages = chat_prompt.format_prompt(input=invoice_example, output=processed_json, input_invoice=input_invoice).to_messages()

    # Create a GPT-4 chat instance
    chat = ChatOpenAI(engine="gpt-4-32k", temperature=0)

    # Generate the chat response using the formatted messages
    resp = chat(messages)

    # Return the content of the response
    return resp.content


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "POST":
        # Handle POST request
        try:
            req_body = req.get_json()
            raw_invoice_data = req_body["raw_invoice_data"]
            
            if not req_body["json_schema"] == 'default':
                json_schema = json.loads(req_body["json_schema"])
            else:
                json_schema = req_body["json_schema"]
            
            sample_json_format = "{ \"line_items\":\"\",\n }"
            if json_schema == "default":
                with open('json_schema_1', 'r') as file:
                    json_schema_1 = json.load(file)
            
            if json_schema == "default":
                with open('json_schema_2', 'r') as file:
                    json_schema_2 = json.load(file)
                
            else:
                # Split properties into two JSON schemas
                properties = json_schema["properties"]
                property_names = list(properties.keys())
                half_length = len(property_names) // 2
                json_schema_1 = {
                "title": json_schema["title"],
                "description": json_schema["description"],
                "type": json_schema["type"],
                "properties": {k: properties[k] for k in property_names[:half_length]},
                "required": [item for item in json_schema["required"] if item in property_names[:half_length]],
                }
                json_schema_2 = {
                "title": json_schema["title"],
                "description": json_schema["description"],
                "type": json_schema["type"],
                "properties": {k: properties[k] for k in property_names[half_length:]},
                "required": [item for item in json_schema["required"] if item in property_names[half_length:]],
                }
            # passing the 2 json schema through LLM
            Output_bifurcated_schemas =process_multiple_schemas(raw_invoice_data,json_schema_1,json_schema_2)
            # joining the 2 outputs
            joined_results = {key: value for d in Output_bifurcated_schemas for key, value in d.items()}
            

            logging.info(joined_results)
            print(joined_results)

            return func.HttpResponse(
                json.dumps(joined_results),
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