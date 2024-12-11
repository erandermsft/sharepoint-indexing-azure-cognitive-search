import os
from gbb_ai.sharepoint_data_extractor import SharePointDataExtractor
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    CorsOptions,
    SearchIndex,
    ComplexField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)

# Define the target directory (change yours)
target_directory = (
    r"C:\Users\erander\source\repos\sharepoint-indexing-azure-cognitive-search"
)

# Check if the directory exists
if os.path.exists(target_directory):
    # Change the current working directory
    os.chdir(target_directory)
    print(f"Directory changed to {os.getcwd()}")
else:
    print(f"Directory {target_directory} does not exist.")




# Instantiate the SharePointDataExtractor client
# The client handles the complexities of interacting with GRAPH API, providing an easy-to-use interface for data extraction.
sp_extractor = SharePointDataExtractor()
sp_extractor.load_environment_variables_from_env_file()

# Authenticate with Microsoft Graph API
sp_extractor.msgraph_auth(use_interactive_session=True)

files_from_root_folder = sp_extractor.retrieve_sharepoint_files_content(
    site_domain=os.environ["SITE_DOMAIN"],
    site_name=os.environ["SITE_NAME"],
    file_formats=["docx", "pdf"],
)

docs = sp_extractor.retrieve_sharepoint_pages_content(site_domain=os.environ["SITE_DOMAIN"],site_name=os.environ["SITE_NAME"])
for doc in docs:
    print(doc['name'])
    print(doc.get('title','No title'))
    # print(doc['url'])
    contents = doc.get('content', {}).get('contents', [])
    for content in contents:
        print(content)
    images = doc.get('content', {}).get('images', [])
    
    for image in images:
        if(image.get('asset_path') != None):
            asset_path = image['asset_path']
            image_bytes = image['image_bytes']
            local_path = os.path.join(target_directory, asset_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(image_bytes)
            print(f"Saved image to {local_path}")

print(files_from_root_folder)