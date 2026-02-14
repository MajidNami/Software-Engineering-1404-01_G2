from django.db import models
from ._utils import new_uuid_str

class CmrComment(models.Model):
    id_comment = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    id_target = models.ForeignKey("crm.CmrTarget", db_column="id_target", on_delete=models.PROTECT)
    user = models.ForeignKey("crm.CmrUser", db_column="user_id", on_delete=models.PROTECT)
    parent_comment = models.ForeignKey("self", db_column="parent_comment_id", null=True, blank=True, on_delete=models.PROTECT)
    body = models.TextField()
    status = models.CharField(max_length=20, default="pending")
    report_count = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cmr_comments"
        managed = False
        indexes = [
            models.Index(fields=["id_target"], name="idx_cmr_comments_target"),
            models.Index(fields=["user"], name="idx_cmr_comments_user"),
            models.Index(fields=["parent_comment"], name="idx_cmr_comments_parent"),
            models.Index(fields=["status"], name="idx_cmr_comments_status"),
        ]

    def __str__(self) -> str:
        return f"Comment {self.id_comment}"
