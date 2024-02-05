from django.urls import path
from communications.views import twilio_webhook_view

urlpatterns = [
    path("twilio/webhook", twilio_webhook_view, name="twilio_webhook"),
]
