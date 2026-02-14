from django.db import models
from ._utils import new_uuid_str

class CmrTarget(models.Model):
    id_target = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    entity_type = models.CharField(max_length=50, null=True, blank=True)
    entity_id = models.CharField(max_length=36)
    target_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "cmr_targets"
        managed = False

    def __str__(self) -> str:
        return self.target_name or self.id_target
