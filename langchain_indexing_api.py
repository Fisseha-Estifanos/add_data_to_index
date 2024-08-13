import os
import time
import asyncio
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from hugging_face_encoders import get_hf_encoder
from langchain_community.vectorstores import Qdrant
from langchain_postgres.vectorstores import PGVector
from langchain.indexes import SQLRecordManager, index
from langchain_community.embeddings import OllamaEmbeddings
from utils import (load_document_data_from_file, setup_langsmith_api_keys,
                   get_config_variable)
setup_langsmith_api_keys()


load_dotenv()
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']


async def initialize_vector_store(use_local_vector_store: bool = True):
    try:
        print("\n\n-----> Index initialization <-----")
        # embedding model setup
        embedding_model_type = get_config_variable(
            parameter_name="embedding_model")
        if embedding_model_type == "openai":
            dimensions = get_config_variable(parameter_name="dimension")
            embedding_model = OpenAIEmbeddings(model='text-embedding-3-large',
                                               dimensions=dimensions)
        elif embedding_model_type == "ollama":
            ollama_embedding_model_name = get_config_variable(
                parameter_name="ollama_embedding_model_name")
            dimensions = get_config_variable(parameter_name="dimension")
            embedding_model = OllamaEmbeddings(
                model=ollama_embedding_model_name)
        elif embedding_model_type == "MedCPT-Article-Encoder":
            embedding_model = await get_hf_encoder(
                hf_encoder_name="ncbi/MedCPT-Article-Encoder")

        # vector store setup
        collection_name = get_config_variable(parameter_name="collection_name")
        namespace = f"qdrant_store_local/{collection_name}"

        vector_store_type = get_config_variable(parameter_name="vector_store")
        if vector_store_type == "qdrant":
            if use_local_vector_store:
                vector_store_url = os.environ['QDRANT_LOCAL_URL']
                qdrant_client = QdrantClient(url=vector_store_url,
                                             timeout=600)
            else:
                vector_store_url = os.environ['QDRANT_CLOUD_URL']
                qdrant_client = QdrantClient(
                    url=vector_store_url,
                    api_key=os.environ['QDRANT_API_KEY'],
                    timeout=600)
            vectorstore = Qdrant(client=qdrant_client,
                                 collection_name=collection_name,
                                 embeddings=embedding_model)
            print("---> Qdrant vector store to be initialized : "
                  + f"{vectorstore}\n---> Type : {type(vectorstore)}")
            print(f"---> vector_store_url: {vector_store_url}")
        elif vector_store_type == "pgvector":
            local_connection = os.environ["LOCAL_DATABASE_URL"]
            vectorstore = PGVector(
                embeddings=embedding_model,
                collection_name=collection_name,
                connection=local_connection,
                use_jsonb=True,
            )
            print("---> PGvector vector store to be initialized : "
                  + f"{vectorstore}\n---> Type : {type(vectorstore)}")
            print(f"---> Connection url: {local_connection}")
        # TODO : add more vector stores here
        elif vector_store_type == "name of vector sore to add":
            pass

        # record manager setup
        record_manager_db_url = get_config_variable(
            parameter_name="record_manager_db_url")
        record_manager = SQLRecordManager(
            namespace, db_url=record_manager_db_url
        )
        record_manager.create_schema()
        print(f"---> collection name: {collection_name}")
        print(f"---> embedding_model: {embedding_model}")
        print(f"---> type: {type(embedding_model)}\n\n")
        return vectorstore, record_manager
    except Exception as ex:
        print('Exception occurred while trying to initialize vector store.\n'
              + f'Error: {ex}')
current_vector_store, current_record_manager = asyncio.run(
    initialize_vector_store(use_local_vector_store=False))


async def load_and_split_documents(path):
    try:
        returned_data = await load_document_data_from_file(document_type='pdf',
                                                           file_name='',
                                                           multi_pdf=True,
                                                           path=path)
        return returned_data
    except Exception as ex:
        print('Exception occurred while trying to load and split documents.\n'
              + f'Error: {ex}')


async def _clear(vectorstore, record_manager):
    try:
        """Hacky helper method to clear content. See the `full` mode section
        to understand why it works."""
        index([], record_manager, vectorstore, cleanup="full",
              source_id_key="source")
        print(f"\n-->Vector store collection {vectorstore.collection_name} "
              + f"that uses the embedding model {vectorstore.embeddings.model}"
              + " cleared successfully")
    except Exception as e:
        print("\nAn error occurred while trying to clear vector store.\n"
              + f"Error: {e}")

# asyncio.run(_clear(vectorstore = current_vector_store,
#                    record_manager = current_record_manager))


async def index_loaded_and_splitted_documents(vectorstore, record_manager):
    try:
        start_time = time.time()
        document_path = "documents/red_nucleus/"
        loaded_and_splitted_documents = await load_and_split_documents(
            path=document_path)
        print('Loading and splitting documents completed in: '
              + f'{round(time.time()-start_time, 2)} seconds')
        return
        start_time = time.time()
        returned_index = index(loaded_and_splitted_documents, record_manager,
                               vectorstore, cleanup="incremental",
                               source_id_key="source")
        print(f'\n\nReturned_index: {returned_index}\nType: '
              + f'{type(returned_index)}')
        print('Indexing and storing vectors completed in: '
              + f'{round(time.time()-start_time, 2)} seconds')
    except Exception as ex:
        print('Exception occurred while trying to index loaded and '
              + f'splitted documents.\nError: {ex}')

asyncio.run(index_loaded_and_splitted_documents(
    vectorstore=current_vector_store, record_manager=current_record_manager))
retriever_object = current_vector_store.as_retriever()
print(f'\n\nretriever object: {retriever_object}\n'
      + f'Type: {type(retriever_object)}')


async def ask_index_similarity_search(query: str = ''):
    try:
        # similarity search
        results = current_vector_store.similarity_search(query)
        print(f'similarity search results: {results}\n'
              + f'Type: {type(results)}\n\n')
    except Exception as ex:
        print(f'Exception occurred while trying to ask index.\nError: {ex}')
# query='The multiple myeloma (MM) cell line MM1.R was purchased from?'
# asyncio.run(ask_index_similarity_search(query))
