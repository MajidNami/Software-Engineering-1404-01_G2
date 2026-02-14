from django.db import models
from ._utils import new_uuid_str

class CmrUser(models.Model):
    id_user = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    is_moderator = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "cmr_users"
        managed = False

    def __str__(self) -> str:
        return f"{self.username} ({self.id_user})"
