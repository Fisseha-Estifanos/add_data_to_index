import os
from PyPDF2 import PdfReader
import pandas as pd

def get_pdf_encoding_software(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            if reader.is_encrypted:
                return "Encrypted"
            info = reader.metadata
            print(f"info : {info}\n")
            return info.producer if info and info.producer else "Unknown"
            # return info.producer
    except Exception as e:
        return str(e)

def list_files_in_directory(directory):
    file_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_type = os.path.splitext(file)[1][1:]  # Get file extension without the dot
            if file.endswith('.pdf'):
                encoding_software = get_pdf_encoding_software(file_path)
            else:
                encoding_software = "not pdf"
            file_info.append((file, root, file_type, encoding_software))
    return file_info

def save_to_excel(file_info, output_path):
    df = pd.DataFrame(file_info, columns=['File Name', 'Directory', 'File Type', 'Encoding Software'])
    df.to_excel(output_path, index=False)


directory_path = '../cellectra_documents/'
# directory_path = 'documents/cel_docs/second_additions/50/'

output_path = 'cellectra_document_details.xlsx'

# List all files with their directories and file types
all_files_info = list_files_in_directory(directory_path)

print("\n\n\nAll Files in Directory:")
for i, (file_name, dir_path, file_type, encoding) in enumerate(all_files_info, 1):
    print(f"{i} : File: {file_name}, Directory: {dir_path}, File Type: {file_type}, Encoding Software: {encoding}\n")

# Save to Excel
save_to_excel(all_files_info, output_path)