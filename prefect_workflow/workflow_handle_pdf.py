
import random
import tempfile
import requests
import json
import os
from pathlib import Path
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact



from markdown_agent.md_paper_metadata_agent import md_paper_metadata_agent, PaperMetadataSchema
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Constants for Google ADK
# APP_NAME = "md_paper_metadata_agent_app"
# USER_ID = "user1234"
# SESSION_ID = "1234"
DJANGO_API_ENDPOINT = os.environ.get("DJANGO_API_ENDPOINT", "https://ai4s-papers-service.deepmd.us/api")

FASTGPT_WEBURL = os.environ.get("FASTGPT_WEBURL", "https://zqibhdki.sealosbja.site")
FASTGPT_DEVELOPER_API_KEY = os.environ.get("FASTGPT_DEVELOPER_API_KEY", "fastgpt-xxx")

MODAL_MARKDOWN_METADATA_AGENT_URL = os.environ.get("MODAL_MARKDOWN_METADATA_AGENT_URL", "https://yfb222333--paper-metadata-agent-analyze-paper-raw-llm-output.modal.run")
DATASET_ID = "684897a43609eeebb2bc7391" # deepmd-papers-md in bja sealos fastgpt

@task
def start_process_webhook_request(webhook_request: dict) -> dict:
    pass

@task
def download_pdf_from_s3(s3_pdf_url: str) -> dict:
    """
    Download PDF from URL to temporary directory
    """
    # Create temporary directory
    temp_workdir = tempfile.mkdtemp(prefix='pdf_download_')
    
    # Extract filename from URL
    filename = os.path.basename(s3_pdf_url)
    
    # Create full file path
    file_path = os.path.join(temp_workdir, filename)
    
    # Download and save file
    response = requests.get(s3_pdf_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    download_result = {
        'temp_workdir': temp_workdir,
        'pdf_file_path': file_path,
    }
    return download_result

@task
def parse_pdf_content(
        pdf_file_path: str,
        temp_workdir: str
    ) -> dict:
    
    with open(pdf_file_path, 'rb') as pdf_file:
        files = {'file': (pdf_file_path, pdf_file, 'application/pdf')}
        data = {'engine': 'marker'}
        
        print(f"calling Modal API to parse PDF... (engine: marker)")
        modal_api_url = "https://yfb222333--pdf-parser-parse-pdf-upload.modal.run"

        api_response = requests.post(
            modal_api_url,
            files=files,
            data=data,
            timeout=300
        )
        api_response.raise_for_status()
        
    # parse response and return markdown content
    result_json = api_response.json()
    markdown_text = result_json['markdown']
    parser_metadata = result_json['metadata']

    markdown_filename = os.path.basename(pdf_file_path) + ".md"
    markdown_path = os.path.join(temp_workdir, markdown_filename)

    with open(markdown_path, "w") as f:
        f.write(markdown_text)

    parse_result = {
        "pdf_file_path": pdf_file_path,
        "markdown_file_path": markdown_path,
        "parser_metadata": parser_metadata
    }
    return parse_result
#%%
def parse_json_text_to_json_obj(json_text: str) -> dict:
    """public json parse logic"""
    # clean possible markdown code block tags

    if json_text.startswith('```json'):
        json_str = json_text.replace('```json', '').replace('```', '').strip()
    else:
        json_str = json_text

    print(f"json_str: {json_str=}")
    # analyze json text to json object, if failed, raise exception
    result_dict = json.loads(json_str)
    
    return result_dict

@task(retries=2, retry_delay_seconds=10)
def agent_generate_paper_metadata(
    markdown_file_path: str,
    modal_markdown_metadata_agent_url: str = MODAL_MARKDOWN_METADATA_AGENT_URL
) -> dict:
    """
    Generate paper metadata using Modal service
    Text parsing happens in Prefect for better monitoring
    """
    # Read markdown content
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Call Modal service - get raw LLM output only
    response = requests.post(modal_markdown_metadata_agent_url, json={
        "markdown_content": markdown_content,
    })
    response.raise_for_status()
    
    result = response.json()
    
    if not result.get("success"):
        raise Exception(f"Modal agent error: {result=}")
    
    # Get raw output from Modal
    raw_output = result["raw_output"]
    print(f"Raw LLM output: {raw_output=}...")  # Log for debugging
    
    # Parse output in Prefect (for monitoring)
    paper_metadata = parse_json_text_to_json_obj(raw_output)
    print(f"paper_metadata: {paper_metadata=}")
    
    return paper_metadata
#%%
@task
def save_pdf_md_to_db(
    pdf_file_path: str,
    markdown_file_path: str, 
    paper_metadata: dict,
    primary_domain: str = 'deepmd',
    api_base_url: str = DJANGO_API_ENDPOINT
) -> dict:
    import requests

    print(f"saving paper to db: {pdf_file_path=} {markdown_file_path=} {paper_metadata=}")
    
    base_data = paper_metadata.copy()
    base_data["primary_domain"] = primary_domain
    
    files = {}
    files['pdf_file'] = open(pdf_file_path, 'rb')
    files['markdown_file'] = open(markdown_file_path, 'rb')
    
    response = requests.post(f"{api_base_url}/papers", data=base_data, files=files)
    
    response.raise_for_status()
    return response.json()
#%%

@task(retries=3, retry_delay_seconds=600)
def upload_to_fastgpt_dataset(
    file_path: str,
    dataset_id: str = DATASET_ID, 
    fastgpt_weburl: str = FASTGPT_WEBURL, 
    fastgpt_developer_api_key: str = FASTGPT_DEVELOPER_API_KEY
) -> dict:
    
    data = {
        "datasetId": dataset_id, 
        "trainingType": "chunk", 
        "chunkSettingMode": "auto",
        "metadata": {}
    }

    with open(file_path, 'rb') as f:
        files = {
            'file': f,
            'data': (None, json.dumps(data))
        }
        response = requests.post(
            f"{fastgpt_weburl}/api/core/dataset/collection/create/localFile", 
            headers={"Authorization": f"Bearer {fastgpt_developer_api_key}"}, 
            files=files
        )
        response.raise_for_status()
    
    upload_result = response.json()
    print(f"upload_to_fastgpt_dataset result: {upload_result=}")
    return upload_result

# @task
# def end_

# @task
# def get_customer_ids() -> list[str]:
#     # Fetch customer IDs from a database or API
#     return [f"customer{n}" for n in random.choices(range(100), k=3)]


# @task
# def get_pdf_content(s3_pdf_url: str) -> str:
#     # Get the content of the PDF file
#     return s3_pdf_url

#%%



@flow(
    flow_run_name="process-{s3_pdf_url}",
    persist_result=True,
    # result_storage="s3-bucket/sealos-bja-prefect-storage-s3",
)
def workflow_handle_pdf_to_db_and_fastgpt(
    s3_pdf_url: str = "https://deepmodeling-docs-r2.deepmd.us/test/test_dpgen.pdf",
    # s3_object_key: str = "test.txt",
    # s3_bucket_endpoint: str = "https://deepmodeling-docs-r2.deepmd.us",
) -> list[str]:

    # s3_object_url = f"{s3_bucket_endpoint}/{s3_object_key}"
    print(f"s3_pdf_url: {s3_pdf_url}")

    download_result = download_pdf_from_s3(s3_pdf_url)

    temp_workdir = download_result['temp_workdir']
    pdf_file_path = download_result['pdf_file_path']
    # markdown_file_path = download_result['markdown_file_path']
    
    parse_result = parse_pdf_content(
        pdf_file_path=pdf_file_path,
        temp_workdir=temp_workdir)

    markdown_file_path = parse_result['markdown_file_path']
    
    paper_metadata = agent_generate_paper_metadata(markdown_file_path=markdown_file_path)

    save_result = save_pdf_md_to_db(
        pdf_file_path=pdf_file_path,
        markdown_file_path=markdown_file_path,
        paper_metadata=paper_metadata)

    upload_result = upload_to_fastgpt_dataset(
        file_path=markdown_file_path,
    )

    # customer_ids = get_customer_ids()
    # Map the process_customer task across all customer IDs
    # results = process_customer.map(customer_ids)
    # summary = summarize_results(results)

    print(f"save_result: {save_result=}")
    print(f"upload_result: {upload_result=}")

    workflow_result = {
        "save_result": save_result,
        "upload_result": upload_result
    }
    # summary = f"Processed PDF: {s3_pdf_url}"

    return workflow_result




if __name__ == "__main__":
    # prefect_getting_started()
    workflow_handle_pdf_to_db_and_fastgpt.serve(
        name="local-deploy-workflow-handle-pdf-to-db-and-fastgpt",
    )

#%%

