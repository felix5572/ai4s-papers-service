from ninja import NinjaAPI, Form, File  
from ninja.files import UploadedFile
from typing import Optional
from .models import Paper
from .schemas import PaperOut, PaperIn, PaperFileUpload


# 创建API实例
api = NinjaAPI(title="Papers API")


@api.get("/papers", response=list[PaperOut])
def list_papers(request):
    """获取所有论文"""
    return Paper.objects.all()  # type: ignore


@api.post("/papers", response=PaperOut)
def create_paper(request, paper: PaperIn):
    """创建新论文 - JSON方式（仅元数据）"""
    return Paper.objects.create(**paper.model_dump())  # type: ignore


@api.post("/papers/upload", response=PaperOut)
def create_paper_upload(request, 
                       paper_data: Form[PaperFileUpload],
                       pdf_file: Optional[UploadedFile] = File(None), # type: ignore
                       markdown_file: Optional[UploadedFile] = File(None)): # type: ignore
    """创建新论文 - 文件上传方式"""
    
    data = paper_data.model_dump()
    
    # 处理上传的PDF文件
    if pdf_file:
        data['pdf_filename'] = pdf_file.name
        data['pdf_content'] = pdf_file.read()
    
    # 处理上传的Markdown文件
    if markdown_file:
        data['markdown_filename'] = markdown_file.name
        data['markdown_content'] = markdown_file.read().decode('utf-8')
    
    return Paper.objects.create(**data)  # type: ignore