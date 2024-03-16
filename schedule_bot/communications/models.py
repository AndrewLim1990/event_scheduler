from django.db import models
from accounts.models import Member
from events.models import Event


class UserContactInfo(models.Model):
    user = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="user_contact_info")
    phone_number = models.CharField(max_length=20, unique=True)


# Create your models here.
class UserEventMessage(models.Model):
    """
    Represents relation between a User and an EventTime
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="user_event_message")
    user = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="user_event_message")
    text = models.TextField()
    has_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    IS_OUTGOING = "outgoing"
    IS_INCOMING = "incoming"
    DIRECTION_CHOICES = [
        (IS_OUTGOING, "Message to user"),
        (IS_INCOMING, "Message from user")
    ]

    direction = models.CharField(choices=DIRECTION_CHOICES, max_length=256, null=True)
