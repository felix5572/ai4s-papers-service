#!/usr/bin/env python3

import os
import tempfile
import requests
import pytest
from workflow_handle_pdf import parse_pdf_content

@pytest.mark.slow
def test_parse_pdf_only():
    """Test parse_pdf_content function"""
    
    # Create temp files
    temp_dir = tempfile.mkdtemp()
    pdf_file = os.path.join(temp_dir, 'test_dpgen.pdf')
    
    # Download PDF
    url = "https://deepmodeling-docs-r2.deepmd.us/test/test_dpgen.pdf"
    response = requests.get(url)
    with open(pdf_file, 'wb') as f:
        f.write(response.content)
    
    # Test function
    try:
        parse_result = parse_pdf_content.fn(pdf_file, temp_dir)
        print(f"parse_result: {parse_result=}")

        # Check result
        assert 'markdown_file_path' in parse_result
        assert os.path.exists(parse_result['markdown_file_path'])
        
        print("✅ Test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_parse_pdf_only() 