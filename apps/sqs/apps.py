from django.apps import AppConfig


class SqsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sqs'
    order = 1
