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