"""Academic Paper Metadata Agent"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from pydantic import BaseModel, Field
from typing import Optional

# MODEL = "gemini-2.5-flash"
MODEL = "gemini-2.5-flash-lite-preview-06-17"

# 文件内容输出模板
FILE_CONTENT_TEMPLATE = """File: {file_path}
Content length: {content_length} characters

Content:
{content}"""

def read_markdown_file(file_path: str, tool_context: ToolContext) -> str:
    """Read markdown file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tool_context.state["markdown_content"] = content
        tool_context.state["file_path"] = file_path
        
        file_content = FILE_CONTENT_TEMPLATE.format(
            file_path=file_path,
            content_length=len(content),
            content=content
        )
        return file_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

class PaperMetadataSchema(BaseModel):
    title: str = Field(description="The title of the academic paper")
    authors: str = Field(description="The authors of the paper (comma-separated)")
    year: int = Field(description="The publication year of the paper")
    abstract: Optional[str] = Field(default=None, description="The abstract or summary of the paper")
    doi: Optional[str] = Field(default=None, description="The DOI of the paper if available")
    journal: Optional[str] = Field(default=None, description="Journal or conference name")
    keywords: Optional[str] = Field(default=None, description="Keywords associated with the paper (comma-separated)")
    url: Optional[str] = Field(default=None, description="URL to the paper if available online")
    arxiv_id: Optional[str] = Field(default=None, description="arXiv identifier if available")


md_paper_metadata_agent_instruction = \
"""\
You are an academic paper metadata agent. When asked to analyze a file:
1. First use the read_markdown_file tool to load the content
2. Extract key bibliographic information and output in JSON format:

{
  "title": "document title",
  "authors": "author names (comma-separated)",
  "year": 2024,
  "abstract": "document abstract/summary",
  "doi": "DOI if available", 
  "journal": "journal or conference name",
  "keywords": "relevant keywords (comma-separated)",
  "url": "paper URL if mentioned",
  "arxiv_id": "arXiv ID if available"
}

For fields not found in the document, omit them from the JSON or use null. Output only valid JSON.
"""

md_paper_metadata_agent = LlmAgent(
    name="md_paper_metadata_agent",
    model=MODEL,
    description="Extract structured metadata from academic papers and research documents",
    instruction=md_paper_metadata_agent_instruction,
    tools=[read_markdown_file]
)


#%% 
# Modal deployment code
import modal
import json
import tempfile

# Create Modal app
app = modal.App("paper-metadata-agent")

# Define the image with required dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install([
    "google-generativeai",
    "google-ai-generativelanguage", 
    "google-adk",
    "pydantic",
])

def create_temp_file_from_content(markdown_content: str) -> str:
    """Create temporary file from markdown content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
        tmp_file.write(markdown_content)
        return tmp_file.name

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("google-api-key")],
    timeout=300,
)
@modal.fastapi_endpoint(method="POST")
async def analyze_paper_raw_llm_output(request_data: dict):
    """
    HTTP endpoint to get raw LLM output (no parsing)
    Expected input: {"markdown_content": "...", "file_path": "optional"}
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    # Get input data
    markdown_content = request_data.get("markdown_content", "")
    
    if not markdown_content:
        return {"success": False, "error": "No markdown content provided"}
    
    # Create temporary file
    temp_file_path = create_temp_file_from_content(markdown_content)
    
    try:
        # Initialize agent
        APP_NAME = "md_paper_metadata_agent_app"
        USER_ID = "modal_service_user"
        SESSION_ID = "modal_session"
        
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )
        runner = Runner(
            agent=md_paper_metadata_agent, 
            app_name=APP_NAME, 
            session_service=session_service
        )
        
        # Run agent
        content = types.Content(
            role='user',
            parts=[types.Part(text=f"analyze {temp_file_path}")]
        )
        
        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        )
        
        # Get response
        raw_output = ''
        async for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                raw_output = event.content.parts[0].text
                break
        
        return {
            "success": True,
            "raw_output": raw_output
        }
        
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)