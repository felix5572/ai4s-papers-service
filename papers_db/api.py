from ninja import NinjaAPI, Form, File  
from ninja.files import UploadedFile
from typing import Optional
from .models import Paper
from .schemas import PaperOut, PaperIn, PaperFileUpload
import httpx
from django.conf import settings
from asgiref.sync import sync_to_async
import hashlib
from django.db import transaction


# Create API instance
api = NinjaAPI(title="Papers API", csrf=False)

# PDF Parser API URL from Django settings
PDF_PARSER_API_URL = settings.PDF_PARSER_API_URL

async def parse_pdf_with_modal_async(origin_content: bytes, filename: str) -> str:
    """Call Modal GPU API to parse PDF content - ASYNC VERSION"""
    print(f'=== DEBUG: Calling Modal GPU API for PDF parsing (async) ===: {filename}')
    print(f'=== DEBUG: PDF_PARSER_API_URL = {PDF_PARSER_API_URL} ===')
    
    if not PDF_PARSER_API_URL or PDF_PARSER_API_URL == "":
        print('=== ERROR: PDF_PARSER_API_URL not set! ===')
        return ''
    
    try:
        print(f'=== DEBUG: Using direct file upload endpoint ===: {PDF_PARSER_API_URL}')
        print(f'=== DEBUG: File size: {len(origin_content)} bytes ===')
        
        # Use async HTTP client with direct file upload
        async with httpx.AsyncClient(timeout=300.0) as client:
            
            # Prepare multipart form data for direct upload
            files = {
                'file': (filename, origin_content, 'application/pdf')
            }
            data = {
                'engine': 'marker'  # or 'docling'
            }
            
            print(f'=== DEBUG: Starting async file upload to Modal API ===')
            
            response = await client.post(PDF_PARSER_API_URL, files=files, data=data)
            
            print(f'=== DEBUG: Modal response status ===: {response.status_code}')
            print(f'=== DEBUG: Modal response headers ===: {dict(response.headers)}')
            
            if response.status_code == 200:
                result = await response.json()
                print(f'=== DEBUG: Modal returned success ===: {result.get("success", False)}')
                print(f'=== DEBUG: Modal response data keys ===: {list(result.keys())}')
                markdown = result.get('markdown', '')
                print(f'=== DEBUG: Markdown length ===: {len(markdown)} characters')
                return markdown
            else:
                print(f'=== ERROR: Modal API failed ===: {response.status_code}')
                print(f'=== ERROR: Modal response text ===: {response.text}')
                return ''
                
    except httpx.TimeoutException as e:
        print(f'=== ERROR: Modal API timeout ===: {str(e)}')
        return ''
    except httpx.ConnectError as e:
        print(f'=== ERROR: Modal API connection error ===: {str(e)}')
        return ''
    except Exception as e:
        print(f'=== ERROR: Modal API exception ===: {type(e).__name__}: {str(e)}')
        import traceback
        print(f'=== ERROR: Traceback ===: {traceback.format_exc()}')
        return ''

def calculate_md5(content: bytes) -> str:
    """Calculate MD5 hash of binary content"""
    return hashlib.md5(content).hexdigest()

def deactivate_duplicate_papers(origin_filemd5: str) -> int:
    """
    Deactivate papers with the same PDF MD5 hash
    Returns the number of deactivated papers
    """
    if not origin_filemd5:
        return 0
    
    # Find papers with same PDF MD5 that are currently active
    duplicate_papers = Paper.objects.filter(
        origin_filemd5=origin_filemd5,
        is_active=True
    )
    
    # Count duplicates before deactivating
    count = duplicate_papers.count()
    
    # Deactivate all duplicates
    if count > 0:
        duplicate_papers.update(is_active=False)
        print(f"=== DEDUP: Deactivated {count} duplicate papers with origin_filemd5={origin_filemd5} ===")
    
    return count


@api.get("/papers", response=list[PaperOut])
def list_papers(request):
    """Get all papers - only active ones"""
    return Paper.objects.filter(is_active=True)  # type: ignore


@api.post("/papers", response=PaperOut)
@transaction.atomic
def create_paper(request):
    """Create new paper - 智能处理JSON或multipart数据"""
    
    # 检查请求类型
    if request.content_type.startswith('multipart/form-data'):
        # Multipart请求 - 处理文件上传
        form_data = request.POST.dict()
        
        # 获取上传的文件
        origin_file = request.FILES.get('origin_file', None) or request.FILES.get('pdf_file', None)
        markdown_file = request.FILES.get('markdown_file')
        
        paper_data = form_data.copy()
        
        # 处理文件内容
        if origin_file:
            # 读取文件内容为字节
            origin_content = origin_file.read()
            paper_data['origin_filename'] = origin_file.name
            paper_data['origin_content'] = origin_content
            
            # Calculate MD5 and handle deduplication
            origin_filemd5 = calculate_md5(origin_content)
            deactivate_duplicate_papers(origin_filemd5)
        
        if markdown_file:
            markdown_content = markdown_file.read()
            paper_data['markdown_content'] = markdown_content
            paper_data['markdown_filename'] = markdown_file.name
            
    else:
        # JSON请求 - 纯元数据
        paper_data = request.json
    
    # 统一创建Paper对象
    return Paper.objects.create(**paper_data)


# @api.post("/papers/upload-parse", response=PaperOut)
# async def create_paper_upload_parse(request, 
#                                    paper_data: Form[PaperFileUpload],
#                                    origin_file: UploadedFile = File(...)): # type: ignore
#     """Create new paper - PDF upload with async parsing to Markdown"""
#     print('=== DEBUG: PDF upload and parse API called ===')
    
#     # Validate file type
#     if not origin_file.name.lower().endswith('.pdf'):
#         raise ValueError("Only PDF files are accepted")
    
#     try:
#         # Read PDF content
#         origin_content = origin_file.read()
#         print(f'=== DEBUG: PDF file size ===: {len(origin_content)} bytes')
        
#         # Prepare data
#         data = paper_data.model_dump()
#         data['origin_filename'] = origin_file.name
#         data['origin_content'] = origin_content
#         data['markdown_content'] = None  # Will be updated later
        
#         # Create paper with deduplication
#         paper = await create_paper_with_dedup()
#         print(f'=== DEBUG: Paper saved successfully ===: Paper ID {paper.id}')
        
#         # Parse PDF asynchronously
#         print('=== DEBUG: Starting async PDF parsing ===')
#         markdown_content = await parse_pdf_with_modal_async(origin_content, origin_file.name)
        
#         # Update markdown content
#         if markdown_content:
#             paper.markdown_content = markdown_content
#             await sync_to_async(paper.save)(update_fields=['markdown_content'])
#             print(f'=== DEBUG: Markdown content updated ===: {len(markdown_content)} characters')
#         else:
#             print('=== WARNING: PDF parsing failed, but PDF saved ===')
        
#         return paper  # type: ignore
        
#     except Exception as e:
#         print(f'=== ERROR: PDF processing exception ===: {str(e)}')
#         raise e