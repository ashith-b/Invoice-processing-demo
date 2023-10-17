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

load_dotenv()

def invoice_processing(json_schema,input_text):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a world class algorithm for extracting information in structured formats."),
            ("human", "Use the given format to extract information from the following input: {input_text}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ]
    )
    llm = ChatOpenAI(engine="gpt_3_5_turbo",temperature=0)
    chain = create_structured_output_chain(json_schema , llm, prompt, verbose=True)
    output = chain.run(input_text)
    return output

def process_multiple_schemas(input_text,json_schema_1,json_schema_2):
    results = []
    
    # Process using the first schema
    result_1 = invoice_processing(json_schema_1, input_text)
    results.append(result_1)
    
    # Process using the second schema
    result_2 = invoice_processing(json_schema_2, input_text)
    results.append(result_2)
    
    return results

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "POST":
        # Handle POST request
        try:
            sample_json_format = "{ \"line_items\":\"\",\n }"
            json_schema_1 = {
                "title": "id",
                "description": "Extract information from invoice",
                "type": "object",
                "properties": {
                    "id": {"title": "ID", "description": "assign a UUID as value to id key", "type": "string"},
                    "name_of_the_company": {"title": "name_of_the_company", "description": "Identify the name of the company", "type": "string"},
                    "address": {"title": "address", "description": "Identify the address of the company", "type": "string"},
                    "issued_to": {"title": "issued_to", "description": "which company was the invoice issued to", "type": "string"},
                    "total_amount": {"title": "total_amount", "description": "What is the total amount of the invoice", "type": "string"},
                    "balance": {"title": "balance", "description": "What is the balance amount of the invoice", "type": "string"},
                },
                "required": ["id", "name_of_the_company","address","issued_to","total_amount","balance","invoice_number","invoice_date","shipment_details","line_items","payment_terms"],
            }
            json_schema_2 = {
                "title": "id",
                "description": "Extract information from invoice",
                "type": "object",
                "properties": {
                    "invoice_number": {"title": "invoice_number", "description": "what is the invoice number", "type": "string"},
                    "invoice_date": {"title": "invoice_date", "description": "what is the date the invoice issued", "type": "string"},
                    "shipment_details": {"title": "shipment_details", "description": "Please extract all the shipment details", "type": "string"},
                    "line_items": {"title": "line_items", "description": "what are line items mentioned and please follow the json pattern of {sample_json_format} format", "type": "string"},
                    "payment_terms": {"title": "payment_terms", "description": "please mention only the payment terms mentioned in the invoice", "type": "string"}
                },
                "required": ["shipment_details","payment_terms", "line_items"],
            }

            req_body = req.get_json()
            raw_invoice_data = req_body["raw_invoice_data"]
            # prompt_str = req_body["prompt"]
            # sample_json_format = req_body["sample_json_format"]

            Output_bifurcated_schemas =process_multiple_schemas(raw_invoice_data,json_schema_1,json_schema_2)
            final_output = {key: value for d in Output_bifurcated_schemas for key, value in d.items()}
            # gpt3_5_json_output = json.loads(final_output)
            logging.info(final_output)
            # req_body = req.get_json()
            # raw_invoice_data = req_body["raw_invoice_data"]
            # prompt_str = req_body["prompt"]
            # sample_json_format = req_body["sample_json_format"]

            # gpt4_prompt = PromptTemplate(
            #     template=prompt_str,
            #     input_variables=["form_input","invoice_json"]
            # )

            # system_message_prompt = SystemMessagePromptTemplate(prompt=gpt4_prompt)

            # chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

            # logging.info(req_body)
            # messages = chat_prompt.format_prompt(form_input=raw_invoice_data,invoice_json=sample_json_format).to_messages()
            # chat = ChatOpenAI(engine="GPT-3_5_turbo",temperature=0)
            # resp = chat(messages)
            # gpt4_json_output = json.loads(resp.content)
            # logging.info(gpt4_json_output)

            return func.HttpResponse(
                json.dumps(final_output),
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
    