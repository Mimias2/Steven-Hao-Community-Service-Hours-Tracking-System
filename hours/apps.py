from django.apps import AppConfig


class HoursConfig(AppConfig):
    name = 'hours'

    # Call signals to create user profile after registration
    def ready(self):
        import hours.signals
