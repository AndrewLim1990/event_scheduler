from django.urls import path
from messages.views import BotView

urlpatterns = [
    path('', BotView),
]