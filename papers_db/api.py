from ninja import NinjaAPI, Form, File  
from ninja.files import UploadedFile
from typing import Optional
from .models import Paper
from .schemas import PaperOut, PaperIn, PaperFileUpload
import httpx
from django.conf import settings
from asgiref.sync import sync_to_async


# Create API instance
api = NinjaAPI(title="Papers API", csrf=False)

# PDF Parser API URL from Django settings
PDF_PARSER_API_URL = settings.PDF_PARSER_API_URL

async def parse_pdf_with_modal_async(pdf_content: bytes, filename: str) -> str:
    """Call Modal GPU API to parse PDF content - ASYNC VERSION"""
    print(f'=== DEBUG: Calling Modal GPU API for PDF parsing (async) ===: {filename}')
    print(f'=== DEBUG: PDF_PARSER_API_URL = {PDF_PARSER_API_URL} ===')
    
    if not PDF_PARSER_API_URL or PDF_PARSER_API_URL == "":
        print('=== ERROR: PDF_PARSER_API_URL not set! ===')
        return ''
    
    try:
        print(f'=== DEBUG: Using direct file upload endpoint ===: {PDF_PARSER_API_URL}')
        print(f'=== DEBUG: File size: {len(pdf_content)} bytes ===')
        
        # Use async HTTP client with direct file upload
        async with httpx.AsyncClient(timeout=300.0) as client:
            
            # Prepare multipart form data for direct upload
            files = {
                'file': (filename, pdf_content, 'application/pdf')
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


@api.get("/papers", response=list[PaperOut])
def list_papers(request):
    """Get all papers"""
    return Paper.objects.all()  # type: ignore


@api.post("/papers", response=PaperOut)
def create_paper(request, paper: PaperIn):
    """Create new paper - JSON metadata only"""
    return Paper.objects.create(**paper.model_dump())  # type: ignore


@api.post("/papers/upload", response=PaperOut)
def create_paper_upload(request, 
                       paper_data: Form[PaperFileUpload],
                       pdf_file: Optional[UploadedFile] = File(None), # type: ignore
                       markdown_file: Optional[UploadedFile] = File(None)): # type: ignore
    """Create new paper - file upload method"""
    
    data = paper_data.model_dump()
    
    # Handle uploaded PDF file
    if pdf_file:
        data['pdf_filename'] = pdf_file.name
        data['pdf_content'] = pdf_file.read()
    
    # Handle uploaded Markdown file
    if markdown_file:
        data['markdown_filename'] = markdown_file.name
        data['markdown_content'] = markdown_file.read().decode('utf-8')
    
    return Paper.objects.create(**data)  # type: ignore


@api.post("/papers/upload-parse", response=PaperOut)
async def create_paper_upload_parse(request, 
                                   paper_data: Form[PaperFileUpload],
                                   pdf_file: UploadedFile = File(...)): # type: ignore
    """Create new paper - PDF upload with async parsing to Markdown"""
    print('=== DEBUG: PDF upload and parse API called ===')
    
    # Validate file type
    if not pdf_file.name.lower().endswith('.pdf'):
        raise ValueError("Only PDF files are accepted")
    
    try:
        # Read PDF content
        pdf_content = pdf_file.read()
        print(f'=== DEBUG: PDF file size ===: {len(pdf_content)} bytes')
        
        # Prepare data
        data = paper_data.model_dump()
        data['pdf_filename'] = pdf_file.name
        data['pdf_content'] = pdf_content
        data['markdown_content'] = None  # Will be updated later
        
        # Save Paper record first
        paper = await sync_to_async(Paper.objects.create)(**data)
        print(f'=== DEBUG: Paper saved successfully ===: Paper ID {paper.id}')
        
        # Parse PDF asynchronously
        print('=== DEBUG: Starting async PDF parsing ===')
        markdown_content = await parse_pdf_with_modal_async(pdf_content, pdf_file.name)
        
        # Update markdown content
        if markdown_content:
            paper.markdown_content = markdown_content
            await sync_to_async(paper.save)(update_fields=['markdown_content'])
            print(f'=== DEBUG: Markdown content updated ===: {len(markdown_content)} characters')
        else:
            print('=== WARNING: PDF parsing failed, but PDF saved ===')
        
        return paper  # type: ignore
        
    except Exception as e:
        print(f'=== ERROR: PDF processing exception ===: {str(e)}')
        raise e