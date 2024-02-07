from communications.models import UserEventMessage


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

    event_id = latest_outgoing_message.event.id

    return event_id
