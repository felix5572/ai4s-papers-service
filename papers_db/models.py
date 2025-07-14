from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone
import hashlib



class Paper(models.Model):
    """
    Core model for storing academic paper metadata and file references.
    Optimized for PostgreSQL with proper indexing and relationships.
    """
    
    # Primary identification - using auto-increment for better performance
    id = models.AutoField(
        primary_key=True,
        help_text="Auto-increment primary key"
    )
    
    # Bibliographic metadata
    title = models.CharField(
        max_length=500,
        help_text="Title of the paper"
    )
    
    authors = models.TextField(
        help_text="Authors of the paper (comma-separated or JSON format)"
    )
    
    doi = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Digital Object Identifier"
    )
    
    year = models.PositiveIntegerField(
        help_text="Publication year"
    )
    
    journal = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Journal or conference name"
    )
    
    abstract = models.TextField(
        blank=True,
        null=True,
        help_text="Abstract of the paper"
    )
    
    keywords = models.TextField(
        blank=True,
        null=True,
        help_text="Keywords associated with the paper"
    )
    
    # External references
    url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="URL to the paper (if available online)"
    )
    
    arxiv_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="arXiv identifier"
    )

    origin_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original PDF filename"
    )

    origin_filemd5 = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="MD5 hash of the PDF file"
    )
    
    # File storage - for PostgreSQL binary storage
    origin_content = models.BinaryField(
        blank=True,
        null=True,
        help_text="PDF file binary content stored in PostgreSQL"
    )

    origin_filelink = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Original URL of the file (optional)"
    )

    
    markdown_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original Markdown filename"
    )

    markdown_filemd5 = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="MD5 hash of the Markdown file"
    )
    
    markdown_content = models.BinaryField(
        blank=True,
        null=True,
        help_text="Markdown file binary content stored in PostgreSQL"
    )

    
    # Metadata and tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the record was last updated"
    )
    
    is_active = models.BooleanField(
        default=True,  # type: ignore
        help_text="Whether this paper record is active"
    )
    
    # Single primary domain classification
    primary_domain = models.CharField(
        max_length=100,
        help_text="Primary research domain (e.g., 'deepmd', 'abacus', 'unimol', 'ai4s')"
    )
    
    # Simple tags as text field (you can also create a separate Tag model)
    tags = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated tags for organization"
    )
    
    class Meta:
        db_table = 'papers'
        verbose_name = 'Paper'
        verbose_name_plural = 'Papers'
        ordering = ['-year', 'title']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['doi']),
            models.Index(fields=['primary_domain']),
            models.Index(fields=['created_at']),
            models.Index(fields=['origin_filemd5']),
            models.Index(fields=['is_active']),
            models.Index(fields=['origin_filemd5', 'is_active']),  # For deduplication queries
        ]
    
    def __str__(self):
        """String representation of the paper."""
        return f"{self.title} ({self.year})"
    
    def get_authors_list(self):
        """Helper method to get authors as a list."""
        if not self.authors:
            return []
        return [author.strip() for author in str(self.authors).split(',')]
    
    def get_keywords_list(self):
        """Helper method to get keywords as a list."""
        if not self.keywords:
            return []
        return [keyword.strip() for keyword in str(self.keywords).split(',')]
    
    def has_files(self):
        """Check if the paper has associated files."""
        return bool(self.origin_content or self.markdown_content)
    
    @property
    def short_title(self):
        """Return a shortened version of the title for display."""
        title_str = str(self.title)
        if len(title_str) > 100:
            return f"{title_str[:97]}..."
        return title_str

    def _calculate_md5(self, content):
        """计算二进制内容的MD5哈希值"""
        md5sum = None
        if content is None:
            md5sum = None
        else:
            md5sum = hashlib.md5(content).hexdigest()
        return md5sum
    
    def save(self, *args, **kwargs):
        """重写save方法，自动计算MD5"""
        # 自动计算原始文件的MD5
        if self.origin_content:
            self.origin_filemd5 = self._calculate_md5(self.origin_content)
        
        # 自动计算Markdown MD5  
        if self.markdown_content:
            self.markdown_filemd5 = self._calculate_md5(self.markdown_content)
            
        super().save(*args, **kwargs)
