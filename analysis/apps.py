"""App configuration for the analysis app."""
from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    name = 'analysis'
    verbose_name = 'Analysis Dashboard'
    default_auto_field = 'django.db.models.AutoField'
