from django.urls import path
from events.views import event_initialization, event_invite, event_detail, create_event_view

urlpatterns = [
    path("api/v1/event-initialization/", event_initialization, name="event_initialization"),
    path('invite/<uuid:uuid>/', event_invite, name='event_invite'),
    path('<int:event_id>/', event_detail, name='event_detail'),
    path('create/', create_event_view, name='create_event'),
]
