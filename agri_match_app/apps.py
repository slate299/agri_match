# apps.py
from django.apps import AppConfig

class AgriMatchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agri_match_app'

    def ready(self):
        # Import signals to ensure they're registered
        import agri_match_app.signals
