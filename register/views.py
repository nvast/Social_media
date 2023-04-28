from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.models import User
from register.retrieve_password import *
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required


@unauthenticated_user
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            login(request, new_user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, 'register/register.html', {"form": form})


@unauthenticated_user
def retrieve(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            password = generate_password()
            retrieve_mail(email, password)
            user.password = make_password(password)
            user.save()
            messages.success(request, 'An email with a new password has been sent to your email address.')
            return redirect("login")
        elif not user:
            messages.error(request, 'Sorry, that email address does not exist.')

    return render(request, "register/retrieve.html", {})


@login_required
def delete_account(request):
    for group in request.user.group_owner.all():
        group.transfer_ownership()

    logout(request)
    request.user.delete()

    return render(request, 'register/register.html', {})
