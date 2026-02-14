import logging
from django.apps import AppConfig
from kombu.exceptions import OperationalError

logger = logging.getLogger(__name__)

class Team2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team2'

    def ready(self):
        from .tasks.indexing import index_all_articles
        try:
            index_all_articles.apply_async(countdown=15, ignore_result=True)
        except OperationalError as e:
            logger.warning(
                "Celery/Redis is not reachable; skipping index_all_articles startup enqueue. (%s)", e
            )
