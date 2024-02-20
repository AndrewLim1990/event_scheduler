from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout
from events.models import UserEvent


def home(request):
    user_id = request.user.id
    context = {}
    if user_id:
        user = User.objects.get(id=user_id)
        user_events = UserEvent.objects.filter(user=user)
        context["user_events"] = user_events
    return render(request, 'home/homepage.html', context)


def logout_view(request):
    # Log out the user
    logout(request)
    # Redirect to homepage or any other page
    return redirect('home')
