from django.http import HttpResponse
from django.shortcuts import render
import os
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


@csrf_exempt
def BotView(request):
    incomming_message = request.POST["Body"]
    sender_name = request.POST["ProfileName"]
    sender_number = request.POST["From"]

    if incomming_message == "Party":
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=f'Hello, {sender_name}. Want to come to my party?!? =)',
            to=sender_number
        )

    return HttpResponse("Hello Andrew....")