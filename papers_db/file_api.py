from ninja import NinjaAPI, Schema
from django.db.models import Count, Q
from typing import Optional
from .models import Paper
from .schemas import PaperOut
from datetime import datetime

# Create separate API instance for file operations
file_api = NinjaAPI(title="Files API", version="1.0.0", urls_namespace="file_api", csrf=False)

# Configuration
PRIMARY_DOMAINS_LIST = [
    "deepmd",
    "abacus", 
    "unimol",
    "ai4s",
    "test",
    "unclassified",
    "unknown"
]

class FileListRequest(Schema):
    parentId: Optional[str] = None
    searchKey: Optional[str] = None

@file_api.post("/v1/file/list")
def list_files(request, payload: FileListRequest):
    """Get file tree structure"""
    
    # Return domain folders - 必须判断：区分返回域列表还是论文列表 
    if not payload.parentId or payload.parentId in ["", "/"]:
        folders = []
        for domain in PRIMARY_DOMAINS_LIST:
            # count = Paper.objects.filter(primary_domain=domain, is_active=True).count()
            folders.append({
                "id": domain + '/',
                "parentId": None,
                "type": "folder",
                "name": domain,
                "updateTime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "createTime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        
        return {
            "code": 200,
            "success": True,
            "message": "",
            "data": folders  # Remove the "files" wrapper
        }
    
    # Return papers in domain - only active ones
    query = Paper.objects.filter(primary_domain=payload.parentId.rstrip('/'), is_active=True)
    
    # Add search filter
    search_key = payload.searchKey or ""
    if search_key:
        query = query.filter(
            Q(title__icontains=search_key) |
            Q(authors__icontains=search_key) |
            Q(keywords__icontains=search_key)
        )
    
    papers = query.order_by('-year', 'title')
    
    files = []
    for paper in papers:
        files.append({
            "id": f"paper_{paper.id}",
            "parentId": payload.parentId,
            # "name": f"{paper.year} {paper.title}",
            "name": f"Paper {paper.id} {paper.origin_filename} {paper.title}",
            "type": "file",
            "updateTime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "createTime": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        })
    
    return {
        "code": 200,
        "success": True, 
        "message": "",
        "data": files  # Remove the "files" wrapper
    }

@file_api.get("/v1/file/content")
def get_file_content(request, id: str):
    """Get single file content"""
    
    # Extract paper id from format "paper_{id}"
    paper_id = id.replace("paper_", "")
    paper = Paper.objects.get(id=paper_id)
    
    # Priority: markdown_content > abstract > PDF preview
    # content = paper.markdown_content or 'Abstract ' + paper.abstract or None
    # content = paper.markdown_content or None
    content = bytes(paper.markdown_content).decode('utf-8') if paper.markdown_content else None

    preview_url = f"/api/file/pdf/{paper.id}" if paper.origin_content else None
    
    return {
        "code": 200,
        "success": True,
        "message": "",
        "data": {
            "title": paper.title,
            "content": content,
            "previewUrl": preview_url
        }
    }

@file_api.get("/pdf/{paper_id}")
def serve_pdf(request, paper_id: int):
    """Serve PDF content"""
    from django.http import HttpResponse
    
    paper = Paper.objects.get(id=paper_id)
    response = HttpResponse(paper.origin_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{paper.origin_filename or "paper.pdf"}"'
    return response

@file_api.get("/v1/file/detail")
def get_file_detail(request, id: str):
    """Get file detailed information"""
    
    # Handle paper file
    if id.startswith("paper_"):
        paper_id = id.replace("paper_", "")
        paper = Paper.objects.get(id=paper_id)
        
        return {
            "code": 200,
            "success": True,
            "message": "",
            "data": {
                **PaperOut.from_orm(paper).model_dump(),
                "parentId": paper.primary_domain,
                "type": "file"
            }
        }
    
    # Handle domain folder
    count = Paper.objects.filter(primary_domain=id).count()
    return {
        "code": 200,
        "success": True,
        "message": "",
        "data": {
            "id": id,
            "parentId": None,
            "name": f"{id} ({count}篇论文)",
            "type": "folder"
        }
    } 