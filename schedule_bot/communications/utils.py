import os
import pytz
import datetime

from communications.models import UserEventMessage
from communications.models import UserContactInfo
from twilio.rest import Client

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


def infer_event_from_messages(user):
    """
    Infers what event the user is responding to based off of past messages

    :param user:
    :return:
    """
    latest_outgoing_message = UserEventMessage.objects.filter(
        user=user,
        direction=UserEventMessage.IS_OUTGOING
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
    user_event_message = UserEventMessage(
        user=user,
        event=event,
        text=text,
        created_at=datetime.datetime.now(tz),
        direction=direction
    )
    user_event_message.save()


def send_message(user, event, text, tz="America/Los_Angeles"):
    """

    :param user:
    :param event:
    :param text:
    :param tz:
    :return:
    """
    user_phone_number = UserContactInfo.objects.get(user=user).phone_number

    # Sends text
    client.messages.create(
        body=text,
        from_="+16593992076",
        to=user_phone_number
    )

    save_event_message(
        user=user,
        event=event,
        text=text,
        direction=UserEventMessage.IS_OUTGOING,
        tz=tz
    )
