import datetime
import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Contributors(TimeStampedModel):
    name = models.CharField(max_length=255, null=True)


class Contributions(TimeStampedModel):
    contributor = models.ForeignKey(Contributors, on_delete=models.CASCADE)
    contribution_date = models.DateField(null=True)
    contribution_amount = models.PositiveIntegerField(null=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        month = int(kwargs.pop("month"))
        year = datetime.date.today().year
        self.contribution_date = datetime.datetime(year, month, 1)
        super().save(*args, **kwargs)


class Expenses(TimeStampedModel):
    added_by = models.CharField(max_length=25)
    date_added = models.DateField(default=datetime.datetime.now().date())
    item_name = models.CharField(max_length=255)
    item_price = models.PositiveIntegerField()
    item_quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField()
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.total_price = int(self.item_price) * int(self.item_quantity)
        super().save(*args, **kwargs)
