from django.urls import path
from events.views import event_initialization, event_invite

urlpatterns = [
    path("api/v1/event-initialization", event_initialization, name="event_initialization"),
    path('invite/<uuid:uuid>', event_invite, name='event_invite')
]
