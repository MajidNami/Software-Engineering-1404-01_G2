from django.db import models

class CmrRatingAggregate(models.Model):
    id_target = models.OneToOneField("crm.CmrTarget", db_column="id_target", primary_key=True, on_delete=models.PROTECT)
    rating_count = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "cmr_rating_aggregates"
        managed = False

    def __str__(self) -> str:
        return f"Aggr {self.id_target_id}: {self.rating_avg}"
