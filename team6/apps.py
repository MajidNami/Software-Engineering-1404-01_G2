from django.apps import AppConfig


class Team6Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team6'

    # ثبت signalها هنگام لود شدن اپلیکیشن
    def ready(self):
        import team6.signals
