import os
import csv
import json
import shutil
import asyncio
from qdrant_client import QdrantClient
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import (PyPDFLoader, TextLoader,
        WebBaseLoader, PyPDFDirectoryLoader, UnstructuredMarkdownLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()


async def load_document_data_from_file(
        document_type: str, file_name: str, multi_pdf: bool = False,
        path: str = "", chunk_size: int = 1500, chunk_overlap: int = 150,
        print_information_of_only_unread_documents: bool = False):
    '''
    A method that loads data from several data type of documents

    Parameters
    ==========
    document_type: string
        The data type of the document
    file_name: string
        The name of the document

    Returns
    =======
    document_result or pages: langchain document
        The document that will be used in the split documents function
    '''
    # step 1 - determine file type
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        if (document_type == 'pdf'):
            if multi_pdf:
                print(f"---> directory_path: {path}")
                loader = PyPDFDirectoryLoader(path=path)
                pages = loader.load_and_split(text_splitter=text_splitter)
                print(f'---> type of loader: {type(loader)}')
                print(f'---> length of pages: {len(pages)}')
                print(f"---> type of pages: {type(pages)}\n\n")
                return pages
            else:
                print(f"---> directory_path: {path}")
                print(f"---> file_name: {file_name}")
                loader = PyPDFLoader(file_path=path + file_name)
                pages = loader.load_and_split(text_splitter=text_splitter)
                if not print_information_of_only_unread_documents:
                    print(f'---> type of loader: {type(loader)}')
                    print(f'---> length of pages: {len(pages)}')
                    print(f"---> type of pages: {type(pages)}\n\n")
                else:
                    if len(pages) == 0:
                        print(f'---> type of loader: {type(loader)}')
                        print(f'---> length of pages: {len(pages)}')
                        print(f"---> type of pages: {type(pages)}\n\n")
                return pages
        elif (document_type == 'txt'):
            loader = TextLoader(file_path=path + file_name)
            pages = loader.load_and_split(text_splitter=text_splitter)
            return pages
        elif (document_type == 'csv'):
            loader = CSVLoader(file_path=path + file_name)
            document_result = loader.load(text_splitter=text_splitter)
            return document_result
    except Exception as e1:
        error_message = f'\nAn error occurred while loading document from file.\nError: {e1}'
        print(error_message)
        return error_message


def get_all_file_names(directory):
    try:
        # Get a list of all files and directories in the specified directory
        entries = os.listdir(directory)
        # Filter out directories, keeping only file names
        files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
        return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


# # # single file for a directory
# directory_to_check = "documents/cel_docs/second_additions/aug_28/"
# # directory_to_check="../cellectra_documents/Journal Articles duplicate all files in one folder/"
# file_names = get_all_file_names(directory=directory_to_check)
# print(f"folder to check : {directory_to_check}")
# print(f"number of files : {len(file_names)}")
# for i, file_name in enumerate(file_names):
#     print(f"#{i+1}")
#     if file_name.endswith('.pdf') | file_name.endswith('.PDF'):
#         document_result = asyncio.run(load_document_data_from_file(
#             document_type="pdf", multi_pdf=False, file_name=file_name,
#             path=directory_to_check,
#             print_information_of_only_unread_documents=True))
#     else:
#         print(f"file {file_name} is not a pdf file.\n\n")


# # multi file for a directory
# # directory_to_check="documents/cel_docs/second_additions/50"
# directory_to_check="../cellectra_documents/Autophagocytosis/"
# document_result = asyncio.run(load_document_data_from_file(document_type="pdf",
#                                          file_name="",
#                                          multi_pdf=True,
#                                          path=directory_to_check))
# print(f"document_result : {document_result}")


def setup_langsmith_api_keys():
    os.environ['LANGCHAIN_API_KEY'] = os.environ["LANGCHAIN_API_KEY"]
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'


def get_config_variable(parameter_name: str = "",
                        file_path: str = "config.json"):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            if parameter_name in data:
                return data[parameter_name]
            else:
                return f"Parameter '{parameter_name}' not found in the config file."
    except FileNotFoundError:
        return "JSON file not found."
    except json.JSONDecodeError:
        return "Error decoding JSON file."


# Function to move all files in sub folder to a root folder
def move_files_to_main_folder(initial_folder):
    # Ensure the initial folder path is absolute
    initial_folder = os.path.abspath(initial_folder)
    print(f"initial_folder : {initial_folder}")

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(initial_folder):
        # Skip the main folder itself
        if root == initial_folder:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            dest_path = os.path.join(initial_folder, file)

            # Move the file to the main folder
            shutil.move(file_path, dest_path)
            print(f'Moved: {file_path} -> {dest_path}')

    # Remove empty directories (if desired)
    for root, dirs, files in os.walk(initial_folder, topdown=False):
        if root != initial_folder:
            try:
                os.rmdir(root)
                print(f'Removed empty directory: {root}')
            except OSError as e:
                print(f'Error removing directory {root}: {e}')

# initial_folder_path = "../cellectra_documents/Journal Articles duplicate all files in one folder/"
# move_files_to_main_folder(initial_folder_path)


# Function to print out the details of files in a directory to a csv file
# function to update to be to be indexed spreadsheet tab
def gather_file_info(folder_path, output_csv):
    # Ensure the folder path is absolute
    folder_path = os.path.abspath(folder_path)

    # Open the CSV file for writing
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow(['file_name', 'extension', 'file_size_MB'])

        # Walk through the directory
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = file
                file_extension = os.path.splitext(file_name)[1]
                file_size_bytes = os.path.getsize(file_path)
                file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes

                # Write the file information to the CSV
                writer.writerow([file_name, file_extension, f"{file_size_mb:.2f} MB"])

    print(f'File information written to {output_csv}')

# folder_path = "documents/cel_docs/second_additions/aug_28/"
# output_csv = f"{folder_path+'file_info.csv'}"
# gather_file_info(folder_path, output_csv)


# # Function to retrieve all points from the source collection
def fetch_all_points(client, collection_name):
    try:
        points = []
        limit = 10000  # Number of points to fetch per request
        offset = None  # Start with no offset

        while True:
            # Fetch points using the scroll method
            print(f"Fetching points from a collection named {collection_name} ...")
            response, offset = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,  # Set to True to include payloads
                with_vectors=True   # Set to True to include vectors if needed
            )
            # Append the fetched points to the list
            points.extend(response)
            # Break if no more points are returned
            if offset is None:
                break
        return points
    except Exception as ex:
        print(f"An error occurred while fetching all points from the collection {collection_name}.\nError : {ex}")


# # Function to migrate one collection to another
def migrate_collection(source_url: str, destination_url: str,
                       source_collection_name: str, batch_size: int = 1000,
                       recreate_on_collision: bool = True):
    # source : https://stackoverflow.com/questions/77733255/how-to-copy-a-collection-from-one-instance-to-another-instance-with-qdrant
    try:
        destination_client = QdrantClient(
                    url=destination_url,
                    api_key=os.environ['QDRANT_API_KEY_RIZZBUZZ'],
                    timeout=600)
        source_client = QdrantClient(url=source_url,
                                    api_key=os.environ['QDRANT_API_KEY'],
                                    timeout=600)
        source_client.migrate(destination_client, [source_collection_name],
                            batch_size=batch_size,
                            recreate_on_collision=recreate_on_collision)
    except Exception as ex:
        print(f"An error occurred while migrating collection.\nError : {ex}")

# migrate_collection(source_collection_name="test_collection",
#                    source_url="https://a15d5b27-c1ba-4ed8-9591-0c8958e40622.us-east4-0.gcp.cloud.qdrant.io",
#                    destination_url="https://d3d17106-811a-4a79-aa4c-1fd5011759a4.us-east4-0.gcp.cloud.qdrant.io")
