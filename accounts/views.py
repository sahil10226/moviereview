from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm

def register(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    else:
        if request.method == "POST":
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                return redirect("accounts:login")  # Redirect to login page after registration
        else:
            form = RegistrationForm()
        return render(request, "accounts/register.html", {"form": form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("main:home")
                else:
                    return render(request, 'accounts/login.html', {"error": "Your account has been disabled."})
            else:
                return render(request, 'accounts/login.html', {"error": "Invalid Username or Password. Try Again."})
        return render(request, 'accounts/login.html')

def logout_user(request):
    logout(request)
    return redirect("main:home")
