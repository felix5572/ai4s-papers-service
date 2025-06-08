import modal
import requests
import time
import json
from fastapi import UploadFile, File, Form
from typing import Optional

# Simple Modal app
app = modal.App("pdf-parser")

# Simple image setup
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "docling",
        "marker-pdf[full]",
        "torch",
        "torchvision", 
        "transformers",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart",  # Required for file uploads
        "requests"
    ])
    .run_commands([
        "apt-get update",
        "apt-get install -y poppler-utils tesseract-ocr"
    ])
    .run_commands([
        "python -c 'import docling; print(\"Docling installed\")'",
        "python -c 'import marker.converters.pdf; print(\"Marker installed\")'",
        "python -c 'import marker.models; print(\"Marker models installed\")'",
        "python -c 'import marker.output; print(\"Marker output installed\")'",
    ])
    .run_commands([
        "python -c 'from marker.converters.pdf import PdfConverter; from marker.models import create_model_dict; print(\"start download model...\"); converter = PdfConverter(artifact_dict=create_model_dict()); print(\"all done!\")'",
    ])
)

# Docling parsing function
@app.function(
   image=image,
   gpu="T4",
   timeout=600,
   memory=8192,
   scaledown_window=40
)
def parse_pdf_with_docling(pdf_url: Optional[str] = None, pdf_content: Optional[bytes] = None) -> dict:
   try:
       from docling.document_converter import DocumentConverter, PdfFormatOption
       from docling.datamodel.base_models import InputFormat
       from docling.datamodel.pipeline_options import PdfPipelineOptions
       import torch
       import tempfile
       import os
       
       if pdf_url:
           print(f"Docling解析PDF (URL): {pdf_url}")
           # 从URL下载PDF
           response = requests.get(pdf_url, timeout=60)
           response.raise_for_status()
           pdf_data = response.content
           filename = pdf_url.split('/')[-1]
       elif pdf_content:
           print(f"Docling解析PDF (直接上传): {len(pdf_content)} bytes")
           pdf_data = pdf_content
           filename = "uploaded.pdf"
       else:
           raise ValueError("需要提供pdf_url或pdf_content")
       
       pdf_size = len(pdf_data)
       
       # 保存到临时文件
       with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
           tmp_file.write(pdf_data)
           pdf_path = tmp_file.name
       
       try:
           pipeline_options = PdfPipelineOptions()
           pipeline_options.do_ocr = True
           pipeline_options.do_table_structure = True
           
           converter = DocumentConverter(
               format_options={
                   InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
               }
           )
           
           start_time = time.time()
           result = converter.convert(pdf_path)
           processing_time = time.time() - start_time
           
           markdown_content = result.document.export_to_markdown()
           page_count = len(result.document.pages) if hasattr(result.document, 'pages') else 1
           
           final_markdown = f"""{markdown_content}

---

*解析信息: {filename} | {pdf_size:,}字节 | {page_count}页 | {processing_time:.1f}秒 | Docling GPU*
"""
           
           return {
               "success": True,
               "markdown": final_markdown,
               "metadata": {
                   "service": "docling-gpu",
                   "file_size": pdf_size,
                   "processing_time": processing_time
               }
           }
           
       finally:
           if os.path.exists(pdf_path):
               os.unlink(pdf_path)
               
   except Exception as e:
       return {
           "success": False,
           "error": str(e),
           "markdown": f"# Docling解析失败\n\n{str(e)}"
       }

# Marker parsing function with configuration - support URL and direct file upload
@app.function(
   image=image,
   gpu="T4",
   timeout=600,
   memory=8192,
   scaledown_window=40
)
def parse_pdf_with_marker(pdf_url: Optional[str] = None, pdf_content: Optional[bytes] = None) -> dict:
   try:
       # 使用新版marker API
       from marker.converters.pdf import PdfConverter
       from marker.models import create_model_dict
       from marker.output import text_from_rendered
       import tempfile
       import os
       
       if pdf_url:
           print(f"Marker解析PDF (URL): {pdf_url}")
           # 从URL下载PDF
           response = requests.get(pdf_url, timeout=60)
           response.raise_for_status()
           pdf_data = response.content
           filename = pdf_url.split('/')[-1]
       elif pdf_content:
           print(f"Marker解析PDF (直接上传): {len(pdf_content)} bytes")
           pdf_data = pdf_content
           filename = "uploaded.pdf"
       else:
           raise ValueError("需要提供pdf_url或pdf_content")
       
       pdf_size = len(pdf_data)
       
       # 保存到临时文件
       with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
           tmp_file.write(pdf_data)
           pdf_path = tmp_file.name
       
       try:
           print("创建Marker转换器...")
           converter = PdfConverter(
               artifact_dict=create_model_dict(),
           )
           
           start_time = time.time()
           print("开始转换PDF...")
           rendered = converter(pdf_path)
           
           print("提取文本和图像...")
           text, _, images = text_from_rendered(rendered)
           
           processing_time = time.time() - start_time
           
           final_markdown = f"""{text}

---

*解析信息: {filename} | {pdf_size:,}字节 | {processing_time:.1f}秒 | Marker GPU | {len(images) if images else 0}图片*
"""
           
           return {
               "success": True,
               "markdown": final_markdown,
               "metadata": {
                   "service": "marker-gpu",
                   "file_size": pdf_size,
                   "processing_time": processing_time,
                   "image_count": len(images) if images else 0
               }
           }
           
       finally:
           if os.path.exists(pdf_path):
               os.unlink(pdf_path)
               
   except Exception as e:
       return {
           "success": False,
           "error": str(e),
           "markdown": f"# Marker解析失败\n\n{str(e)}"
       }

# 原有的JSON API - 支持URL方式
@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def parse_pdf_api(item: dict):
   """
   PDF解析API - JSON格式，支持URL
   """
   pdf_url = item.get("pdf_url") or item.get("file_url")
   if not pdf_url:
       return {"success": False, "error": "需要pdf_url参数"}
   
   # 路由选择
   engine = item.get("engine", "marker")  
   
   if engine == "marker":
       return parse_pdf_with_marker.remote(pdf_url=pdf_url)
   else:
       return parse_pdf_with_docling.remote(pdf_url=pdf_url)

# 新增：文件上传API - 支持直接传文件
@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def parse_pdf_upload(
    file: UploadFile = File(...),
    engine: str = Form("marker")
):
    """
    PDF解析API - 文件上传格式，支持直接传PDF文件
    """
    try:
        # 读取上传的文件内容
        pdf_content = file.file.read()
        
        if not pdf_content:
            return {"success": False, "error": "文件内容为空"}
        
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            return {"success": False, "error": "只支持PDF文件"}
        
        print(f"收到文件上传: {file.filename}, 大小: {len(pdf_content)} bytes, 引擎: {engine}")
        
        # 路由到不同引擎
        if engine == "marker":
            return parse_pdf_with_marker.remote(pdf_content=pdf_content)
        else:
            return parse_pdf_with_docling.remote(pdf_content=pdf_content)
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"文件处理失败: {str(e)}",
            "markdown": f"# 文件上传解析失败\n\n{str(e)}"
        }

# 健康检查
@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def health():
   return {
       "status": "healthy",
       "service": "dual-engine-pdf-parser",
       "engines": ["docling", "marker"],
       "api_modes": ["url", "file_upload"],
       "version": "2.2.0",
       "timestamp": time.time()
   }

# 本地测试
@app.local_entrypoint()
def test():
   test_url = "https://objectstorageapi.bja.sealos.run/w4tywxqg-deepmodeling-docs/deepmd/major/DeePMD-kit.pdf"
   
   print("Testing Docling with URL...")
   result1 = parse_pdf_with_docling.remote(pdf_url=test_url)
   print(f"Docling URL: {result1['success']}")
   
   print("Testing Marker with URL...")
   result2 = parse_pdf_with_marker.remote(pdf_url=test_url)
   print(f"Marker URL: {result2['success']}")
   
   # 测试文件上传方式
   try:
       print("Testing file upload (if PDF exists)...")
       with open("test.pdf", "rb") as f:
           pdf_content = f.read()
       result3 = parse_pdf_with_marker.remote(pdf_content=pdf_content)
       print(f"Marker Upload: {result3['success']}")
   except FileNotFoundError:
       print("No test.pdf found, skipping file upload test")