from django.urls import path
from . import views

urlpatterns = [
    path(r"login", views.user_login, name="login"),
    path(r"register/", views.register, name="register"),
    path(r"", views.home, name="home"),
    path(r"change-password", views.change_password, name="change-password"),
    path(r"logout", views.user_logout, name="logout"),
]
