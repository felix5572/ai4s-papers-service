#!/usr/bin/env python3

import os
import tempfile
import pytest
from workflow_handle_pdf import upload_to_fastgpt_dataset

test_content = """# Test Paper

## Abstract
This is a test paper for testing FastGPT upload functionality.

## Authors
Test Author

## Keywords
test, fastgpt, upload

## Content
This is test content for the FastGPT dataset upload.
"""

# @pytest.mark.slow
def test_upload_to_fastgpt():
    """Test upload_to_fastgpt_dataset function"""
    
    # Create temp markdown file
    temp_dir = tempfile.mkdtemp()
    md_file = os.path.join(temp_dir, 'test_paper.md')
    
    # Create test markdown content
    
    
    with open(md_file, 'w') as f:
        f.write(test_content)
    
    # Print environment variables before upload
    print("Environment variables:")
    print(f"FASTGPT_WEBURL: {os.getenv('FASTGPT_WEBURL', 'NOT SET')}")
    print(f"FASTGPT_DEVELOPER_API_KEY: {os.getenv('FASTGPT_DEVELOPER_API_KEY', 'NOT SET')}")
    print(f"DATASET_ID: {os.getenv('DATASET_ID', 'NOT SET (using default)')}")
    print(f"Markdown file: {md_file}")
    
    # Test function
    try:
        result = upload_to_fastgpt_dataset.fn(md_file)
        
        # Check result
        assert result is not None
        assert isinstance(result, dict)
        
        print("✅ Test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_upload_to_fastgpt() 