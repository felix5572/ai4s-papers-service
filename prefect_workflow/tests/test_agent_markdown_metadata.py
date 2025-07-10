#!/usr/bin/env python3

import tempfile
import os
import pytest
import shutil
from workflow_handle_pdf import agent_generate_paper_metadata
from workflow_handle_pdf import MODAL_MARKDOWN_METADATA_AGENT_URL

test_markdown_content = """\
# Test Paper

## Abstract
This is a test paper for testing the sync function.

## Authors
Test Author

## Year
2024

## Keywords
test, sync, function

## Content
This is a test paper for testing the sync agent function.
"""

def test_sync_function():
    # 检查环境变量
    import os
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"GOOGLE_API_KEY: {'SET' if api_key else 'NOT SET'}")
    
    # 创建临时测试文件
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, 'test.md')
    
    # 写入测试内容
    with open(test_file, 'w') as f:
        f.write(test_markdown_content)
    
    print(f"test markdown file: {test_file}")
    
    try:
        # test sync function
        result = agent_generate_paper_metadata.fn(
            markdown_file_path=test_file,
            modal_markdown_metadata_agent_url=MODAL_MARKDOWN_METADATA_AGENT_URL
        )
        print(f"result: {type(result)=} {result=}")
        
    except Exception as e:
        print(f"error: {e}")
        raise e
    
    finally:
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 

# GOOGLE_API_KEY="${GOOGLE_API_KEY}" pytest test_agent_markdown_metadata.py -s -v