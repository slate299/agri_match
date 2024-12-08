from django.apps import AppConfig


class AgriMatchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agri_match_app'

    def ready(self):
        import agri_match_app.signals  # Import the signals.py to register the signal
