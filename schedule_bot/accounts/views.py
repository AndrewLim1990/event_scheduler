from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from accounts.forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            _, user_has_acc = form.save()
            if user_has_acc:
                return redirect('existing_account_already')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
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


class ExistingAccountAlready(LoginView):
    template_name = 'accounts/existing_account_already.html'

    def get_success_url(self):
        # You can include any logic here to determine the redirect URL
        return reverse_lazy('home')
