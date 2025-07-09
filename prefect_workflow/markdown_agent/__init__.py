"""Markdown Document Analyzer Agent"""

from .md_paper_metadata_agent import md_paper_metadata_agent

# ADK需要这个名称
root_agent = md_paper_metadata_agent

__all__ = ["markdown_analyzer", "root_agent"] 