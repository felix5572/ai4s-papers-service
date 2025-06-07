from django.apps import AppConfig


class PapersDbConfig(AppConfig):
    """Configuration for the papers_db application."""
    
    # Basic app identification
    name = 'papers_db'  # App name (must match directory name)
    label = 'papers_db'  # Unique label for this app
    verbose_name = 'Academic Papers Database'  # Human-readable name
    
    # Database configuration
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore  # Default primary key type
    
    # Advanced configuration options
    # path = None  # Auto-detected app path (commented out to let Django auto-detect)
    
    def ready(self):
        """
        Called when Django starts up and the app is ready.
        Use this for initialization code like registering signals.
        """
        # Import signals or other initialization code here
        # Example: from . import signals
        pass  # TODO: Add initialization logic if needed
    
    # Example of other methods you can override:
    
    def get_models(self, include_auto_created=False, include_swapped=False):
        """Get all models for this app."""
        return super().get_models(include_auto_created, include_swapped)
    
    def get_model(self, model_name, require_ready=True):
        """Get a specific model by name."""
        return super().get_model(model_name, require_ready)
