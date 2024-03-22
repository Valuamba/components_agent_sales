from django.apps import AppConfig


class DailyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'daily_app'  # Unique label for the daily app
    name = 'daily'
