from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Event(models.Model):
    """
    Represents a specific event
    """
    name = models.CharField(max_length=512, null=True, default=None)
    # On delete, must choose new host:
    host_member = models.ForeignKey(User, on_delete=models.PROTECT, related_name="events_hosted")
    members = models.ManyToManyField(User, null=True, default=None, related_name="events_invited")


class EventTime(models.Model):
    """
    Represents a proposed event time
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
