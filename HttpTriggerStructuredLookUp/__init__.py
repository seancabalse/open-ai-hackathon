import logging

import azure.functions as func
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

from langchain.vectorstores.azuresearch import AzureSearch

from langchain.chat_models import AzureChatOpenAI


def init_embeddings():
    logging.info(f"init_embeddings")
    vector_store_address: str = 'https://globecogse.search.windows.net'
    # vector_store_password: str = 'Jk3aMWZNUeOdjiPZxDWgaWS4lXOY001YQcRTZXVUbZAzSeCiFO0l'
    vector_store_password: str = 'JsKG2IrQ0IjDWB2vWcCt4sZTYK6mdjzIMc1dGMLtaJAzSeDkp8lI'

    index_name: str = 'globevectorindex'
    
    logging.info("Creating AI Embeddings...")
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            openai_api_type="azure",
            openai_api_version="2023-03-15-preview",
            openai_api_base="https://globeopenai.openai.azure.com/",
            openai_api_key="314a741f06914946b61ff593a05f7b49",
            chunk_size=1)
    
    logging.info("Creating Azure Search....")
    vector_store: AzureSearch = AzureSearch(
        openai_api_type="azure",
        openai_api_version="2023-03-15-preview",
        openai_api_base="https://globeopenai.openai.azure.com/",
        openai_api_key="314a741f06914946b61ff593a05f7b49",
        azure_search_endpoint=vector_store_address,
        azure_search_key=vector_store_password,
        index_name=index_name,
        embedding_function=embeddings.embed_query)
    
    logging.info("Done creating embeddings and vectore store.")
    return embeddings, vector_store


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(f'{context.function_directory}')
    
    prompt = req.params.get('prompt')
    if not prompt:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            prompt = req_body.get('prompt')

    if prompt:
        
        embeddings, vector_store = init_embeddings()
        
        model = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_version="2023-03-15-preview",
            openai_api_base="https://globeopenai.openai.azure.com/",
            openai_api_key="314a741f06914946b61ff593a05f7b49",
            temperature=0.25,
            deployment_name="gpt-35-turbo"
        )
        qa = RetrievalQA.from_llm(
            llm=model,
            retriever=vector_store.as_retriever(),
            verbose=True
        )

        logging.info(f"qa: {qa}")
        
        result = qa.run(f"{prompt}")
        logging.info(f"Result: {result}")
        
        return func.HttpResponse(
             result,
             status_code=200
        )
        
        
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
