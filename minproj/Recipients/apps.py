from django.apps import AppConfig


class RecipientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Recipients'

    def ready(self):
        import Recipients.signals
