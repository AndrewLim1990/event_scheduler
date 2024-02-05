from django.db import models
from django.contrib.auth.models import User
from events.models import Event


# Create your models here.
class UserEventMessage(models.Model):
    """
    Represents relation between a User and an EventTime
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="user_event_message")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_event_message")
    text = models.TextField()
    has_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    IS_OUTGOING = "outgoing"
    IS_INCOMING = "incoming"
    DIRECTION_CHOICES = [
        (IS_OUTGOING, "Message to user"),
        (IS_INCOMING, "Message from user")
    ]

    explicit_response = models.CharField(choices=DIRECTION_CHOICES, max_length=256, null=True)
