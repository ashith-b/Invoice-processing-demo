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

template_1 = '''
System: You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Relevance measures how well the answer addresses the main aspects of the question, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between zero to one using the following rating scale:
Zero stars : the answer is wrong or incomplete
One stars : the answer is completely correct

This rating value should always be an integer between 0 and 1. So the rating produced should be 0 or 1

Example 1:

context: TAX INVOICE\nIntegrated Living\nPO BOX 2567\nDANGAR NSW 2309\nAUSTRALIA\nInvoice Date\n1 Aug 2022\nInvoice Number\nINV-0716\nReference\nJanet Sissions\nABN\n41 539 697 361\nInside Out Property And\nGarden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nItem\nDescription\nQuantity\nUnit Price\nGST\nAmount AUD\nCASE\nCase Manager\nSusan Swanson\n1.00\n0.00\n0.00\nCLIENT\nClient Name and Address\nJanet Sissions\n11/287-289 Charlestown RD\nCharlestown\n1.00\n0.00\n0.00\nMOULD\nMould Removal\nAttend clients home remove on main\nbedroom lounge room and spare bed room.\nJob completed 29.07.2022\n1.00\n120.00\n10%\n120.00\nSubtotal\n120.00\nTOTAL GST 10%\n12.00\nTOTAL AUD\n132.00\nDue Date: 15 Aug 2022\nInvoices payable within 14 days to the following bank account;\nInside Out Property And Garden Maintenance\nBSB 650 000\nACC 525 656 002\nInside Out\nPROPERTY &\nGARDEN\nMaintenance\n-X ---\nPAYMENT ADVICE\nTo:\nInside Out Property And Garden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nCustomer\nIntegrated Living\nInvoice Number\nINV-0716\nAmount Due\n132.00\nDue Date\n15 Aug 2022\nAmount Enclosed\nEnter the amount you are paying above\n

question: Identify the name of the company
answer: Moonlighting Connects Pty Ltd

stars : 1

Example 2:

context: TAX INVOICE\nIntegrated Living\nPO BOX 2567\nDANGAR NSW 2309\nAUSTRALIA\nInvoice Date\n1 Aug 2022\nInvoice Number\nINV-0716\nReference\nJanet Sissions\nABN\n41 539 697 361\nInside Out Property And\nGarden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nItem\nDescription\nQuantity\nUnit Price\nGST\nAmount AUD\nCASE\nCase Manager\nSusan Swanson\n1.00\n0.00\n0.00\nCLIENT\nClient Name and Address\nJanet Sissions\n11/287-289 Charlestown RD\nCharlestown\n1.00\n0.00\n0.00\nMOULD\nMould Removal\nAttend clients home remove on main\nbedroom lounge room and spare bed room.\nJob completed 29.07.2022\n1.00\n120.00\n10%\n120.00\nSubtotal\n120.00\nTOTAL GST 10%\n12.00\nTOTAL AUD\n132.00\nDue Date: 15 Aug 2022\nInvoices payable within 14 days to the following bank account;\nInside Out Property And Garden Maintenance\nBSB 650 000\nACC 525 656 002\nInside Out\nPROPERTY &\nGARDEN\nMaintenance\n-X ---\nPAYMENT ADVICE\nTo:\nInside Out Property And Garden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nCustomer\nIntegrated Living\nInvoice Number\nINV-0716\nAmount Due\n132.00\nDue Date\n15 Aug 2022\nAmount Enclosed\nEnter the amount you are paying above\n
question: Identify the name of the company
answer: Sunlight Connects Pty Ltd

stars : 0

Example 3:

context: TAX INVOICE\nIntegrated Living\nPO BOX 2567\nDANGAR NSW 2309\nAUSTRALIA\nInvoice Date\n1 Aug 2022\nInvoice Number\nINV-0716\nReference\nJanet Sissions\nABN\n41 539 697 361\nInside Out Property And\nGarden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nItem\nDescription\nQuantity\nUnit Price\nGST\nAmount AUD\nCASE\nCase Manager\nSusan Swanson\n1.00\n0.00\n0.00\nCLIENT\nClient Name and Address\nJanet Sissions\n11/287-289 Charlestown RD\nCharlestown\n1.00\n0.00\n0.00\nMOULD\nMould Removal\nAttend clients home remove on main\nbedroom lounge room and spare bed room.\nJob completed 29.07.2022\n1.00\n120.00\n10%\n120.00\nSubtotal\n120.00\nTOTAL GST 10%\n12.00\nTOTAL AUD\n132.00\nDue Date: 15 Aug 2022\nInvoices payable within 14 days to the following bank account;\nInside Out Property And Garden Maintenance\nBSB 650 000\nACC 525 656 002\nInside Out\nPROPERTY &\nGARDEN\nMaintenance\n-X ---\nPAYMENT ADVICE\nTo:\nInside Out Property And Garden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nCustomer\nIntegrated Living\nInvoice Number\nINV-0716\nAmount Due\n132.00\nDue Date\n15 Aug 2022\nAmount Enclosed\nEnter the amount you are paying above\n
question: what is the invoice number
answer: 8540

stars : 0

Example 4:

context: TAX INVOICE\nIntegrated Living\nPO BOX 2567\nDANGAR NSW 2309\nAUSTRALIA\nInvoice Date\n1 Aug 2022\nInvoice Number\nINV-0716\nReference\nJanet Sissions\nABN\n41 539 697 361\nInside Out Property And\nGarden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nItem\nDescription\nQuantity\nUnit Price\nGST\nAmount AUD\nCASE\nCase Manager\nSusan Swanson\n1.00\n0.00\n0.00\nCLIENT\nClient Name and Address\nJanet Sissions\n11/287-289 Charlestown RD\nCharlestown\n1.00\n0.00\n0.00\nMOULD\nMould Removal\nAttend clients home remove on main\nbedroom lounge room and spare bed room.\nJob completed 29.07.2022\n1.00\n120.00\n10%\n120.00\nSubtotal\n120.00\nTOTAL GST 10%\n12.00\nTOTAL AUD\n132.00\nDue Date: 15 Aug 2022\nInvoices payable within 14 days to the following bank account;\nInside Out Property And Garden Maintenance\nBSB 650 000\nACC 525 656 002\nInside Out\nPROPERTY &\nGARDEN\nMaintenance\n-X ---\nPAYMENT ADVICE\nTo:\nInside Out Property And Garden Maintenance\n65 Kula Rd\nMEDOWIE NSW 2318\nAUSTRALIA\nCustomer\nIntegrated Living\nInvoice Number\nINV-0716\nAmount Due\n132.00\nDue Date\n15 Aug 2022\nAmount Enclosed\nEnter the amount you are paying above\n
question: what is the invoice number
answer: 1769

stars : 1
context: {context}

Use the context to score the stars for 
{question}
{answer}
stars:
'''

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


def format_json_output(schema, data):
    """
    Formats the given data based on the provided JSON schema.

    Parameters:
    schema (dict): JSON schema describing the expected structure of the data.
    data (dict): Data to be formatted based on the schema.

    Returns:
    list: A list of dictionaries containing formatted data with titles, descriptions, and corresponding answers.
    """

    # Initialize an empty list to store the formatted output
    result = []

    # Iterate through the properties defined in the schema
    for key, value in schema["properties"].items():
        # Check if the property is an array
        if value["type"] == "array":
            # Get the nested data for the array property
            nested_data = data.get(key, [])
            # Get the schema for items in the array
            nested_schema = value["items"]
            # Process each item in the array recursively
            for item in nested_data:
                nested_result = format_json_output(nested_schema, item)
                result.extend(nested_result)
        else:
            # Extract title, description, and answer for non-array properties
            title = value.get("title")
            description = value.get("description")
            answer = data.get(key, "Not Provided")
            # Store the formatted data in a dictionary and append to the result list
            result.append({'title': title, 'description': description, 'answer': answer})

    # Return the formatted output as a list of dictionaries
    return result


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
                    input_variables=["context", "question", "answer"]
                )
    system_message_prompt = SystemMessagePromptTemplate(prompt=gpt3_5_prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Initialize lists to store evaluation scores and wrong answers
    scoring = []
    wrong_answers = []
    
    # Iterate through the formatted extracted information
    for i in format_json_output:
        # Generate messages using the predefined prompts and extracted information
        messages = chat_prompt.format_prompt(context=raw_invoice_data, question=i['description'], answer=i['answer']).to_messages()
        chat = ChatOpenAI(engine="gpt-4-32k", temperature=0)
        
        # Generate response using GPT-3.5 Turbo
        resp = chat(messages)

        # Evaluate the response
        if resp.content == '0':
            # If the response indicates incorrect answer, store the answer and title
            wrong_answers.append({i['title']: i['answer']})
        # Store the response content (evaluation score) in the scoring list
        scoring.append(resp.content)

    # Return the evaluation scores and wrong answers as a tuple
    return scoring, wrong_answers

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
                json_schema_1 = {
                                    "title": "Invoice",
                                    "description": "Extract information from an invoice",
                                    "type": "object",
                                    "properties": {
                                        "Vendor No.": {
                                            "title": "Vendor No.",
                                            "description": "Identify the ID of the vendor",
                                            "type": "string"
                                        },
                                        "Vendor Name": {
                                            "title": "Vendor Name",
                                            "description": "Identify the name of the vendor",
                                            "type": "string"
                                        },
                                        "Account No.": {
                                            "title": "Account No.",
                                            "description": "Identify the account number",
                                            "type": "string"
                                        },
                                        "Property Address": {
                                            "title": "Property Address",
                                            "description": "Identify the Property Address",
                                            "type": "string"
                                        },
                                        "Posted Purchase Invoice": {
                                            "title": "Posted Purchase Invoice",
                                            "description": "Identify the Posted Purchase Invoice",
                                            "type": "string"
                                        },
                                        "Invoice Date": {
                                            "title": "Invoice Date",
                                            "description": "Identify the Invoice Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge Start Date": {
                                            "title": "Fixed Charge Start Date",
                                            "description": "Identify the Fixed Charge Start Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge End Date": {
                                            "title": "Fixed Charge End Date",
                                            "description": "Identify the Fixed Charge End Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge for Water Service": {
                                            "title": "Fixed Charge for Water Service",
                                            "description": "Identify the Fixed Charge for Water Service",
                                            "type": "string"
                                        },
                                        "Fixed Charge for Waste Water": {
                                            "title": "Fixed Charge for Waste Water",
                                            "description": "Identify the Fixed Charge for Waste Water",
                                            "type": "string"
                                        },
                                        "Total Fixed Charges": {
                                            "title": "Total Fixed Charges",
                                            "description": "Identify the Total Fixed Charges",
                                            "type": "string"
                                        }
                                    },
                                    "required": ["Vendor No.", "Vendor Name", "Account No.", "Property Address", "Posted Purchase Invoice", "Invoice Date", "Fixed Charge Start Date", "Fixed Charge End Date", "Fixed Charge for Water Service", "Fixed Charge for Waste Water", "Total Fixed Charges"]
                                }

                json_schema_2 = {
                                    "title": "Invoice",
                                    "description": "Extract information from an invoice",
                                    "type": "object",
                                    "properties": {
                                        "line_items": {
                                            "title": "Line Items",
                                            "description": "Details of line items such as Water Oncharging",
                                            "type": "array",
                                            "items": {
                                                "title": "Line Item",
                                                "description": "Extract information from each line item of Water Oncharging",
                                                "type": "object",
                                                "properties": {
                                                    "Reading From (Date)": {
                                                        "title": "Reading From (Date)",
                                                        "description": "Identify the Reading From (Date)",
                                                        "type": "string"
                                                    },
                                                    "Reading To (Date)": {
                                                        "title": "Reading To (Date)",
                                                        "description": "Identify the Reading To (Date)",
                                                        "type": "string"
                                                    },
                                                    "No. of Days": {
                                                        "title": "No. of Days",
                                                        "description": "Identify the number of Days",
                                                        "type": "string"
                                                    },
                                                    "Meter No.": {
                                                        "title": "Meter No.",
                                                        "description": "Identify the Meter No.",
                                                        "type": "string"
                                                    },
                                                    "Last Reading": {
                                                        "title": "Last Reading",
                                                        "description": "Identify the Last Reading",
                                                        "type": "string"
                                                    },
                                                    "This Reading": {
                                                        "title": "This Reading",
                                                        "description": "Identify the This Reading",
                                                        "type": "string"
                                                    },
                                                    "Net Meter Reading": {
                                                        "title": "Net Meter Reading",
                                                        "description": "Identify the Net Meter Reading",
                                                        "type": "string"
                                                    },
                                                    "Rate 1": {
                                                        "title": "Rate 1",
                                                        "description": "Identify the Rate 1",
                                                        "type": "string"
                                                    },
                                                    "Usage 1": {
                                                        "title": "Usage 1",
                                                        "description": "Identify the Usage 1",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 1": {
                                                        "title": "Usage Cost 1",
                                                        "description": "Identify the Usage Cost 1",
                                                        "type": "string"
                                                    },
                                                    "Rate 2": {
                                                        "title": "Rate 2",
                                                        "description": "Identify the Rate 2",
                                                        "type": "string"
                                                    },
                                                    "Usage 2": {
                                                        "title": "Usage 2",
                                                        "description": "Identify the Usage 2",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 2": {
                                                        "title": "Usage Cost 2",
                                                        "description": "Identify the Usage Cost 2",
                                                        "type": "string"
                                                    },
                                                    "Rate 3": {
                                                        "title": "Rate 3",
                                                        "description": "Identify the Rate 3",
                                                        "type": "string"
                                                    },
                                                    "Usage 3": {
                                                        "title": "Usage 3",
                                                        "description": "Identify the Usage 3",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 3": {
                                                        "title": "Usage Cost 3",
                                                        "description": "Identify the Usage Cost 3",
                                                        "type": "string"
                                                    },
                                                    "Total Usage": {
                                                        "title": "Total Usage",
                                                        "description": "Identify the Total Usage",
                                                        "type": "string"
                                                    },
                                                    "Other Water Charges": {
                                                        "title": "Other Water Charges",
                                                        "description": "Identify the Other Water Charges",
                                                        "type": "string"
                                                    },
                                                    "Other Water Credits": {
                                                        "title": "Other Water Credits",
                                                        "description": "Identify the Other Water Credits",
                                                        "type": "string"
                                                    },
                                                    "Total Charge": {
                                                        "title": "Total Charge",
                                                        "description": "Identify the Total Charge",
                                                        "type": "string"
                                                    }
                                                },
                                                "required": ["Reading From (Date)", "Total Charge"]
                                            }
                                        }
                                    },
                                    "required": ["Vendor No.", "Vendor Name", "Account No.", "Property Address", "Posted Purchase Invoice", "Invoice Date", "Fixed Charge Start Date", "Fixed Charge End Date", "Fixed Charge for Water Service", "Fixed Charge for Waste Water", "Total Fixed Charges"]
                                }
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
            formatted_question_answer_pairs = format_json_output(json_schema_1, joined_results) + format_json_output(json_schema_2, joined_results)
            print(formatted_question_answer_pairs)
            # performing Evaluation
            evaluation_results = evaluation(template_1,formatted_question_answer_pairs,raw_invoice_data)
            Incorrect_results = evaluation_results[1]
            relevance_scoring = sum(int(number) for number in evaluation_results[0])/len(evaluation_results[0])
            # If average is less than 1, set it to 0
            if relevance_scoring < 1:
                relevance_scoring = 0
            print(relevance_scoring)
            final_output = {
                "invoice_result" : joined_results,
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