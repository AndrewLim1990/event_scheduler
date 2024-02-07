from communications.models import UserEventMessage
import datetime
import pytz


def infer_event_from_messages(user):
    """
    Infers what event the user is responding to based off of past messages

    :param user:
    :return:
    """
    latest_outgoing_message = UserEventMessage.objects.filter(
        user=user,
        explicit_response=UserEventMessage.IS_OUTGOING
    ).order_by('-created_at').first()

    event = latest_outgoing_message.event

    return event


def save_event_message(user, event, text, direction, tz="America/Los_Angeles"):
    """
    Saves communication between app and user

    :param user:
    :param event:
    :param text:
    :param direction:
    :param tz:
    :return:
    """
    tz = pytz.timezone(tz)
    user_event_message = UserEventMessage.create(
        user=user,
        event=event,
        text=text,
        created_at=datetime.datetime.now(tz),
        direction=direction
    )
    user_event_message.save()
