from django.db import models
from ._utils import new_uuid_str

class CmrAiAnalysis(models.Model):
    id_analysis = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    comment = models.ForeignKey("crm.CmrComment", db_column="id_comment", null=True, blank=True, on_delete=models.PROTECT)
    media = models.ForeignKey("crm.CmrMedia", db_column="id_media", null=True, blank=True, on_delete=models.PROTECT)
    spam_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    toxicity_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    model_version = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "cmr_ai_analysis"
        managed = False
