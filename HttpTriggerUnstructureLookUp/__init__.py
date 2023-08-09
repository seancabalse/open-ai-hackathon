import logging
import json

import azure.functions as func
from sqlalchemy.engine import Engine, create_engine
import pymysql
from langchain.chains import create_sql_query_chain
import mysql.connector

from langchain.chat_models import AzureChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.schema import HumanMessage, SystemMessage 



def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(f'{context.function_directory}')
    
    logging.info("Printing file ----- HERE -----")
    f = open(f'{context.function_directory}/DigiCertGlobalRootCA.crt.pem', "r")
    logging.info(f.read())
    
    prompt = req.params.get('prompt')
    if not prompt:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            prompt = req_body.get('prompt')

    if prompt:
        
        db_user="glbadmin"
        db_password="Globe2023"
        db_host="globemysqlservers.mysql.database.azure.com"
        db_name='ms_training_mysql'
        open_api_type="azure"
        open_api_version="2023-03-15-preview"
        open_api_base="https://globeopenai.openai.azure.com/"
        open_api_key="314a741f06914946b61ff593a05f7b49"
        
        ssl_args = {
        "ssl_ca": f'{context.function_directory}/DigiCertGlobalRootCA.crt.pem'
        }

        logging.info("Creating engine...")
        engine = create_engine("mysql+mysqlconnector://{db_username}:{db_pass}@globemysqlservers.mysql.database.azure.com:3306/ms_training_mysql".format(db_username=db_user, db_pass=db_password),
            connect_args=ssl_args,
            echo=True
        )
        
        logging.info("Done creating enginee....")
        
        engine._connection_cls
        
        
            
        
        logging.info(" Creating database...")
        database = SQLDatabase(engine=engine)


        logging.info(" Creating Model ----")
        model = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_version="2023-03-15-preview",
            openai_api_base="https://globeopenai.openai.azure.com/",
            openai_api_key="314a741f06914946b61ff593a05f7b49",
            temperature=0,
            deployment_name="gpt-35-turbo",
        
         )
    
        logging.info("Creating sql query chain.....")
        chain = create_sql_query_chain(model, database)
        
        logging.info("Chain invoke....")
        result = chain.invoke({"question": prompt})
        
        logging.info("Result: {ci_result}".format(ci_result=result))
        
        prompt_response = database.run(result)
        logging.info(f"Prompt response: {prompt_response}")
        
        model_response = model(
        [
        SystemMessage(content=f"""You are a database expert that answers the question: {prompt}.
                       After running the query: {prompt}, you got the answer: {prompt_response}.
                       Your task is give the answer in simple language."""),
        HumanMessage(content=prompt)
        ]
        )
        
        logging.info(f"Model response: {model_response.content}")
        
        json_result = json.dumps({
            'text': model_response.content
        })
        
        return func.HttpResponse(
             json_result,
             status_code=200
        )
        
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
