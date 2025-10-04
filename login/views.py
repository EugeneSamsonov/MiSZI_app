from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from user.forms import UserChangePasswordForm, UserRegistrationForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q


from user.models import User


def user_login(request):
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(
                request=request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy("home"))
            else:
                login_form.add_error("password", "Неверная пара логин/пароль")
    else:
        login_form = UserLoginForm()

    return render(request, "login/login.html", {"login_form": login_form})


@login_required(login_url=reverse_lazy("login"))
def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password1"])
            new_user.save()
            # login(request, new_user)
            # return HttpResponseRedirect(reverse_lazy("home"))
            user_form.add_error("username", "User created")

    else:
        user_form = UserRegistrationForm()

    return render(request, "login/register.html", {"user_form": user_form})


@login_required(login_url=reverse_lazy("login"))
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy("login"))


@login_required(login_url=reverse_lazy("login"))
def home(request):
    if request.user.is_admin:
        users = User.objects.filter(~Q(pk=request.user.pk)).all().order_by("username")
        return render(request, "login/home.html", {"users": users})
    return render(request, "login/home.html")


@login_required(login_url=reverse_lazy("login"))
def change_password(request):
    if request.method == "POST":
        change_password_form = UserChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            cd = change_password_form.cleaned_data
            user = User.objects.get(pk=request.user.pk)
            if user.check_password(cd["old_password"]):
                user.set_password(cd["new_password1"])
                user.save()
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return HttpResponseRedirect(reverse_lazy("home"))
            else:
                change_password_form.add_error("old_password", "Invalid password")

    else:
        change_password_form = UserChangePasswordForm()

    return render(
        request,
        "login/chage-password.html",
        {"change_password_form": change_password_form},
    )
