from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Event(models.Model):
    """
    Represents a specific event
    """
    name = models.CharField(max_length=512, null=True, default=None)


class EventTime(models.Model):
    """
    Represents a proposed event time
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_times")
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()


class UserEvent(models.Model):
    """
    Represents a junction table between User and Event
    """
    WAITING_RESPONSE = "waiting_response"
    WAITING_SUGGESTION = "waiting_suggestion"
    WAITING_VALIDATION = "waiting_validation"
    WAITING_FOR_OTHERS = "waiting_for_others"
    IS_ATTENDING = "is_attending"
    IS_NOT_ATTENDING = "is_not_attending"
    STATE_CHOICES = [
        (WAITING_RESPONSE, "Waiting for attendance from user"),
        (WAITING_SUGGESTION, "Waiting for date suggestion from user"),
        (WAITING_VALIDATION, "Waiting for date validation from user"),
        (WAITING_FOR_OTHERS, "Waiting for other users to respond to suggestions"),
        (IS_ATTENDING, "Is able to attend event"),
        (IS_NOT_ATTENDING, "Has elected to not attend event"),
    ]
    state = models.CharField(choices=STATE_CHOICES, max_length=256, null=True, default=None)

    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="users", on_delete=models.CASCADE)
    is_required = models.BooleanField()
    is_host = models.BooleanField()
