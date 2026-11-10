from django.apps import AppConfig


class BackendApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend_api'
    verbose_name = 'Backend REST API Engine'
