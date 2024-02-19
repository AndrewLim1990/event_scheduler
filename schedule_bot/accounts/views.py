from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


class MyLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        # You can include any logic here to determine the redirect URL
        return reverse_lazy('home')
