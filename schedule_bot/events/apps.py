from django.apps import AppConfig
from django.db.models.signals import post_save


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        #  Implicitly connect a signal handlers decorated with @receiver.
        from events import signals
