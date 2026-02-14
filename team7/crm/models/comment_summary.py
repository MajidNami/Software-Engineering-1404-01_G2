from django.db import models
from ._utils import new_uuid_str

class CmrCommentSummary(models.Model):
    id_summary = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    id_target = models.ForeignKey("crm.CmrTarget", db_column="id_target", on_delete=models.PROTECT)
    summary_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cmr_comment_summaries"
        managed = False
