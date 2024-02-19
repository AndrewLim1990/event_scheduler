from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout


def home(request):
    return render(request, 'home/homepage.html')


def logout_view(request):
    # Log out the user
    logout(request)
    # Redirect to homepage or any other page
    return redirect('home')
