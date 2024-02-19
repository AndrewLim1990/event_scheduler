from django.urls import path
from .views import signup_view, MyLoginView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', MyLoginView.as_view(), name='login')
]
