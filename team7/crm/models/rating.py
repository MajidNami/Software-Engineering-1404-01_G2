from django.db import models
from ._utils import new_uuid_str

class CmrRating(models.Model):
    id_rating = models.CharField(max_length=36, primary_key=True, default=new_uuid_str)
    id_target = models.ForeignKey("crm.CmrTarget", db_column="id_target", on_delete=models.PROTECT)
    user = models.ForeignKey("crm.CmrUser", db_column="user_id", on_delete=models.PROTECT)
    rating_value = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cmr_ratings"
        managed = False
        indexes = [
            models.Index(fields=["id_target"], name="idx_cmr_ratings_target"),
            models.Index(fields=["user"], name="idx_cmr_ratings_user"),
        ]

    def __str__(self) -> str:
        return f"Rating {self.rating_value} by {self.user_id}"
