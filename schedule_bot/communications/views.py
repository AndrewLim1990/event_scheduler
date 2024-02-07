import json
import os

from django.http import JsonResponse
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from events.models import UserEvent
from events.finite_state_machine import UserEventMachine
from django.contrib.auth.models import User
from communications.utils import infer_event_from_messages
from communications.models import UserEventMessage


client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


@csrf_exempt
@require_POST
def twilio_webhook_view(request):
    """
    Receives incoming text from user through Twilio webhook

    :param request:
    :return:
    """
    # Obtains message information
    data = json.loads(request.body)
    phone_number = data.get("From")
    text = data.get("Body")
    print(f"From: {phone_number}")
    print(f"Message: {text}")

    user = User.objects.filter(user_contact_info__whatsapp_phone_number=phone_number)
    event_id = infer_event_from_messages(user)
    # save_message(user, text, direction=UserEventMessage.IS_INCOMING)

    # Find the latest outgoing message to the user to determine event
    event_id = 5

    # Get the UserEvent
    user_event = UserEvent.objects.get(
        user__username=user,
        event_id=event_id
    )
    user_event_machine = UserEventMachine(user_event)
    user_event_machine.process_input_text(text)

    # If new state is waiting_for_others, send off initial text to next person "no_communication"
    if user_event.state == UserEvent.WAITING_FOR_OTHERS:
        next_user_event = UserEvent.objects.filter(
            event=user_event.event,
            state=UserEvent.NO_COMMUNICATION
        )
        if next_user_event:
            next_user_event = next_user_event[0]
            next_user_event_machine = UserEventMachine(next_user_event)
            next_user_event_machine.send_initial_text()

    # Return a JSON response
    return JsonResponse({
        "stats": "success",
        "message": "Webhook received successfully"
    })
