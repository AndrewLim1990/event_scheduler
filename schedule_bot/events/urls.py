from django.urls import path
from events.views import event_initialization

urlpatterns = [
    path("api/v1/event-initialization", event_initialization, name="event_initialization"),
]
