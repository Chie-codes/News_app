from django.apps import AppConfig
import importlib


class NewsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_app"

    def ready(self):
        """
        Safely import signals to ensure they are registered when Django starts.
        Wrapping in try/except avoids issues during migrations or when models aren't ready.
        """
        try:
            importlib.import_module("news_app.signals")
        except ImportError:
            pass
