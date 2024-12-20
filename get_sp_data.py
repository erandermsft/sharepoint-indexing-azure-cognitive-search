import os
import json
from gbb_ai.sharepoint_data_extractor import SharePointDataExtractor
from markitdown import MarkItDown
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
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


token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

openai_client = AzureOpenAI(api_version="2024-02-01",
    azure_endpoint=os.environ["OPEN_API_BASE"],
    azure_ad_token_provider=token_provider
)


# Instantiate the MarkItDown client
md = MarkItDown(llm_client=openai_client, llm_model="gpt-4-evals")





# Instantiate the SharePointDataExtractor client
# The client handles the complexities of interacting with GRAPH API, providing an easy-to-use interface for data extraction.
sp_extractor = SharePointDataExtractor()
sp_extractor.load_environment_variables_from_env_file()

# Authenticate with Microsoft Graph API
sp_extractor.msgraph_auth(use_interactive_session=False)

# files_from_root_folder = sp_extractor.retrieve_sharepoint_files_content(
#     site_domain=os.environ["SITE_DOMAIN"],
#     site_name=os.environ["SITE_NAME"],
#     file_formats=["docx", "pdf"],
# )
#Get all pages that have been modified in the last 24 hours
docs = sp_extractor.retrieve_sharepoint_pages_content(site_domain=os.environ["SITE_DOMAIN"],site_name=os.environ["SITE_NAME"], minutes_ago=1440)
for doc in docs:
    # print(doc['name'])
    print(doc.get('title','No title'))
    # print(doc['url'])
    contents = doc.get('content', {}).get('contents', [])
    # get json string from contents array
    html_document = f"<html><body><h1>{doc.get('title')}</h1>\n" + "\n".join(contents) + "\n</body></html>"
    #write html document to file
    html_path = os.path.join(target_directory, doc.get('name').replace(".aspx",".html"))
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, 'w') as f:
        f.write(html_document)

    content_md = md.convert(html_path)
    md_path = html_path.replace(".html", ".md")
    with open(md_path, 'w') as f:
        f.write(content_md.text_content)
    
   
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


            markdown = md.convert(local_path)
            #add image reference using file name from local_path inside markdown
            # ![2800131800-camping_big_2](2800131800-camping_big_2.jpeg)
            markdown.text_content = f"![{os.path.basename(local_path)}]({os.path.basename(local_path)})\n\n{markdown.text_content}"
            #Use os.path to get the file name without the extension
            file_base, _ = os.path.splitext(local_path)
            markdown_path = f"{file_base}.md"
            with open(markdown_path, 'w') as f:
                f.write(markdown.text_content)
            print(f"Saved image to {local_path}")

