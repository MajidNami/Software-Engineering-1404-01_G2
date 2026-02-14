from django.db import models
from ._utils import new_uuid_str

class CmrReport(models.Model):
    id_report = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    reporter = models.ForeignKey("crm.CmrUser", db_column="reporter_user_id", on_delete=models.PROTECT)
    reason = models.CharField(max_length=50, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")  # pending|valid|invalid
    comment = models.ForeignKey("crm.CmrComment", db_column="id_comment", null=True, blank=True, on_delete=models.PROTECT)
    media = models.ForeignKey("crm.CmrMedia", db_column="id_media", null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "cmr_reports"
        managed = False
        indexes = [
            models.Index(fields=["reporter"], name="idx_cmr_reports_reporter"),
            models.Index(fields=["status"], name="idx_cmr_reports_status"),
            models.Index(fields=["comment"], name="idx_cmr_reports_comment"),
            models.Index(fields=["media"], name="idx_cmr_reports_media"),
        ]

    def __str__(self) -> str:
        return f"Report {self.id_report} ({self.status})"
