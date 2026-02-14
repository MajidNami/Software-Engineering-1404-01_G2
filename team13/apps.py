import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def _ensure_team13_default_admin(sender, **kwargs):
    """پس از migrate: کاربر admin@gmail.com را با get_or_create بگیر/بساز و در TeamAdmin ثبت کن."""
    if kwargs.get("using") != "team13":
        return
    try:
        from django.contrib.auth import get_user_model
        from .models import TeamAdmin

        User = get_user_model()
        email = "admin@gmail.com"
        password = "admin"
        normalized_email = (email or "").strip().lower()
        if hasattr(User.objects, "normalize_email"):
            normalized_email = User.objects.normalize_email(normalized_email)

        user, created = User.objects.db_manager("default").get_or_create(
            email=normalized_email,
            defaults={"email": normalized_email},
        )
        if created:
            user.set_password(password)
            user.save(using="default")

        TeamAdmin.objects.using("team13").get_or_create(
            user_id=str(user.id),
            defaults={"user_id": str(user.id)},
        )
    except Exception as e:
        logger.warning("Team13 default admin setup skipped or failed: %s", e, exc_info=True)


class Team13Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team13'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_ensure_team13_default_admin, sender=self)
