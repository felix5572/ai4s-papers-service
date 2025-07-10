#!/usr/bin/env python3

import tempfile
import os
import shutil
import pytest
from workflow_handle_pdf import save_pdf_md_to_db


# @pytest.mark.slow
def test_save_function():
    """Test the save_pdf_md_to_db function with sample data"""
    
    # Create temporary test files
    temp_dir = tempfile.mkdtemp()
    pdf_file = os.path.join(temp_dir, 'test_paper.pdf')
    md_file = os.path.join(temp_dir, 'test_paper.pdf.md')
    
    # Create mock files
    with open(pdf_file, 'wb') as f:
        f.write(b'%PDF-1.4 fake pdf content for testing')
    
    with open(md_file, 'w') as f:
        f.write('# Test Paper\n\n## Abstract\nThis is a test paper for function testing.')
    
    # Create test metadata
    test_metadata = {
        'title': 'Test Paper',
        'authors': 'Test Author',
        'year': 2024,
        'abstract': 'This is a test paper'
    }
    
    print("Test files prepared successfully")
    print(f"PDF file: {pdf_file}")
    print(f"Markdown file: {md_file}")
    print(f"Metadata: {test_metadata}")
    
    try:
        # Call the function to test
        result = save_pdf_md_to_db.fn(
            pdf_file_path=pdf_file,
            markdown_file_path=md_file,
            paper_metadata=test_metadata,
            primary_domain='test'
        )
        print(f"Function result: {result}")
        
    except Exception as e:
        print(f"Function execution error: {e}")
        # Re-raise for pytest to catch
        raise
    
    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Temporary files cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 