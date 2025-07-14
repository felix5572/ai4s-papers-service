#!/usr/bin/env python3

import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from workflow_handle_pdf import workflow_handle_pdf_to_db_and_fastgpt

@pytest.mark.slow
def test_workflow_locally():
    """Simple local test for the workflow"""
    
    # Set environment variable if needed
    if not os.getenv('GOOGLE_API_KEY'):
        print("Warning: GOOGLE_API_KEY not set")
    
    # Test with default PDF URL
    test_url = "https://deepmodeling-docs-r2.deepmd.us/test/test_dpgen.pdf"
    # test_url = "https://deepmodeling-docs-r2.deepmd.us/deepmd-kit/deepmd-materials.pdf"
    
    print(f"Testing workflow with URL: {test_url}")
    
    try:
        # Call the flow directly as a regular function
        result = workflow_handle_pdf_to_db_and_fastgpt(s3_object_url=test_url)
        print(f"Workflow completed successfully!")
        print(f"Result: {result}")
        return result
        
    except Exception as e:
        print(f"Workflow failed: {e}")
        raise

if __name__ == "__main__":
    test_workflow_locally()

# GOOGLE_API_KEY="${GOOGLE_API_KEY}" FASTGPT_DEVELOPER_API_KEY="${FASTGPT_DEVELOPER_API_KEY}" pytest test_workflow_handle_pdf.py -s -v
