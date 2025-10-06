from django.apps import AppConfig
import importlib


class NewsAppConfig(AppConfig):
    """
    Configuration class for the 'news_app' Django application.

    This class specifies the default auto field type and ensures that
    signals are registered when Django starts.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_app"

    def ready(self):
        """
        Import signals to ensure they are registered with Django's signal framework.

        Wrapping in try/except avoids import errors during migrations
        or when models are not yet fully loaded.
        """
        try:
            importlib.import_module("news_app.signals")
        except ImportError:
            pass
