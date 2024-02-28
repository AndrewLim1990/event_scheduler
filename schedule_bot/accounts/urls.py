from django.urls import path
from .views import signup_view, MyLoginView, ExistingAccountAlready

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('existing_account_already/', ExistingAccountAlready.as_view(), name='existing_account_already')
]
