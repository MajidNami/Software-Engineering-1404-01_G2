from django.db import models
from ._utils import new_uuid_str

class CmrMedia(models.Model):
    id_media = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    id_target = models.ForeignKey("crm.CmrTarget", db_column="id_target", on_delete=models.PROTECT)
    user = models.ForeignKey("crm.CmrUser", db_column="user_id", on_delete=models.PROTECT)
    media_type = models.CharField(max_length=10, null=True, blank=True)  # image|video
    object_key = models.TextField(null=True, blank=True)
    public_url = models.TextField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    report_count = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cmr_media"
        managed = False
        indexes = [
            models.Index(fields=["id_target"], name="idx_cmr_media_target"),
            models.Index(fields=["user"], name="idx_cmr_media_user"),
            models.Index(fields=["status"], name="idx_cmr_media_status"),
        ]

    def __str__(self) -> str:
        return f"Media {self.id_media}"
