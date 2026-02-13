from django.apps import AppConfig


class Team2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team2'

    def ready(self):
        from .tasks.indexing import index_all_articles
        index_all_articles.apply_async(countdown=15)
