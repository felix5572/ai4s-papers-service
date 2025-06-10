from django.contrib import admin
from .models import Paper


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    """Admin configuration for Paper model."""
    
    # List page display
    list_display = ['id', 'title', 'year', 'primary_domain', 'journal', 'pdf_filename', 'pdf_filemd5', 'markdown_filename', 'markdown_filemd5', 'is_active', 'created_at', 'updated_at']
    list_display_links = ['title']  # Which fields are clickable
    list_editable = ['is_active']  # Quick edit fields
    list_filter = ['primary_domain', 'year', 'is_active']  # Right sidebar filters
    list_select_related = []  # Optimize queries for related fields
    list_per_page = 25  # Pagination
    list_max_show_all = 200  # Max items on "Show all" page
    
    # Search functionality
    search_fields = ['title', 'authors', 'doi']
    search_help_text = "Search by title, authors, or DOI"
    
    # Ordering and sorting
    ordering = ['-year', 'title']
    sortable_by = ['title', 'year', 'created_at']  # Which columns are sortable
    
    # Form configuration
    fields = None  # Use fieldsets instead
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'authors', 'year', 'journal')
        }),
        ('Content', {
            'fields': ('abstract', 'keywords', 'primary_domain', 'tags'),
            'classes': ('wide',)  # CSS classes for styling
        }),
        ('Files & Links', {
            'fields': ('pdf_content', 'pdf_filename', 'markdown_content', 'url', 'doi', 'arxiv_id')
        }),
        ('Settings', {
            'fields': ('is_active',),
            'classes': ('collapse',)  # Collapsible section
        })
    )
    
    # Field behavior
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {}  # Auto-populate fields based on others
    autocomplete_fields = []  # Enable autocomplete for foreign keys
    raw_id_fields = []  # Use raw ID widget for foreign keys
    radio_fields = {}  # Use radio buttons instead of select
    filter_horizontal = []  # Better widget for many-to-many
    filter_vertical = []  # Alternative many-to-many widget
    
    # Advanced options
    save_as = False  # Enable "Save as new" button
    save_as_continue = True  # Redirect after "Save as new"
    save_on_top = False  # Show save buttons at top
    preserve_filters = True  # Keep filters after operations
    inlines = []  # Inline related models
    
    # Permissions
    def has_add_permission(self, request):
        """Control add permission."""
        return True  # TODO: Implement custom logic
    
    def has_change_permission(self, request, obj=None):
        """Control change permission."""
        return True  # TODO: Implement custom logic
    
    def has_delete_permission(self, request, obj=None):
        """Control delete permission."""
        return True  # TODO: Implement custom logic
    
    def has_view_permission(self, request, obj=None):
        """Control view permission."""
        return True  # TODO: Implement custom logic
    
    # Batch actions
    actions = ['make_active', 'delete_selected_papers']
    actions_on_top = True  # Show actions at top
    actions_on_bottom = False  # Show actions at bottom
    actions_selection_counter = True  # Show selection counter
    
    def make_active(self, request, queryset):
        """Batch activate selected papers."""
        pass  # TODO: Implement activation logic
    make_active.short_description = "Mark selected papers as active"  # type: ignore
    
    # Custom methods for list display
    def short_title(self, obj):
        """Display shortened title."""
        return obj.short_title
    short_title.short_description = "Title"  # type: ignore
    short_title.admin_order_field = 'title'  # type: ignore
