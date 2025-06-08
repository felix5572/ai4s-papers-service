from ninja import NinjaAPI, Schema
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from typing import Optional, Dict, Any
from .models import Paper
from .schemas import PaperOut

# Create separate API instance for file operations
file_api = NinjaAPI(title="Files API", version="1.0.0", urls_namespace="file_api")

# Domain configuration - add your domains here
PRIMARY_DOMAINS_LIST = [
    "deepmd",
    "abacus", 
    "unimol",
    "ai4s",
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
            count = Paper.objects.filter(primary_domain=domain).count()
            folders.append({
                "id": domain,
                "parentId": None,
                "type": "folder",
                "name": domain,
                "updateTime":datetime.now().isoformat(),
                "createTime":datetime.now().isoformat()
                # "count": count
            })
        
        return {
            "code": 200,
            "success": True,
            "message": "",
            "data": {"files": folders}
        }
    
    # Return papers in domain
    query = Paper.objects.filter(primary_domain=payload.parentId)
    
    # Add search filter
    search_key = payload.searchKey or ""
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
            "name": f"{paper.year} {paper.title}",
            "type": "file",
            "year": paper.year,
            "authors": paper.authors
        })
    
    return {
        "code": 200,
        "success": True, 
        "message": "",
        "data": {"files": files}
    }

@file_api.get("/v1/file/content")
def get_file_content(request, id: str):
    """Get single file content"""
    
    # Extract paper id from format "paper_{id}"
    paper_id = id.replace("paper_", "")
    paper = Paper.objects.get(id=paper_id)
    
    # Priority: markdown_content > abstract > PDF preview
    content = paper.markdown_content or 'Abstract ' + paper.abstract or None
    preview_url = f"/api/file/pdf/{paper.id}" if paper.pdf_content else None
    
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
    response = HttpResponse(paper.pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{paper.pdf_filename or "paper.pdf"}"'
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