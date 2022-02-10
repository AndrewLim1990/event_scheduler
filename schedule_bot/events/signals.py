from django.db.models.signals import post_save
from django.dispatch import receiver
from events.models import EventTime
from events.models import UserEventTime
from events.models import UserEvent
from events.utils import get_all_event_participants


@receiver(post_save, sender=EventTime)
def event_time_post_save_handler(sender, instance, **kwargs):
    """
    Creates a UserEventTime linking the saved EventTime to each participant within
    the event

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # Get all event participants
    event_time = instance
    event = event_time.event
    participants = get_all_event_participants(event)
    for participant in participants:
        UserEventTime.objects.get_or_create(
            user=participant,
            event_time=event_time
        )


@receiver(post_save, sender=UserEvent)
def user_event_post_save_handler(sender, instance, **kwargs):
    """
    Creates a UserEventTime linking the added User to each proposed EventTime

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    # Get all event participants
    user_event = instance
    user = user_event.user
    event = user_event.event
    event_times = EventTime.objects.filter(event=event)

    for event_time in event_times:
        UserEventTime.objects.get_or_create(
            user=user,
            event_time=event_time
        )
