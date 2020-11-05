from django.apps import AppConfig


class XendappConfig(AppConfig):
    name = 'xendapp'

    def ready(self):
        from .utils import start
        start()
