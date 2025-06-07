from ninja import ModelSchema, Schema
from django.core.files.uploadedfile import UploadedFile
from .models import Paper
from typing import Optional


class PaperOut(ModelSchema):
    """输出Paper数据 - 不包含文件内容"""
    class Meta:
        model = Paper
        fields = "__all__"
        exclude = ["pdf_content", "markdown_content", "abstract"] 


class PaperIn(ModelSchema):
    """创建Paper - JSON方式"""
    class Meta:
        model = Paper
        fields = "__all__"
        exclude = ["pdf_content", "pdf_filename", "markdown_filename", "markdown_content", "id", "created_at", "updated_at"] 


class PaperFileUpload(ModelSchema):
    """创建Paper - 文件上传方式的元数据（不包含文件字段）"""
    class Meta:
        model = Paper
        fields = "__all__"
        exclude = ["pdf_content", "markdown_content", "id", "created_at", "updated_at"]