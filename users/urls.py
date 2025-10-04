from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.home, name="home"),

    path(r"login/", views.user_login, name="login"),
    path(r"register/", views.register, name="register"),
    path(r"change-password/", views.change_password, name="change-password"),
    path(r"logout", views.user_logout, name="logout"),
    
    path(r"update-user", views.user_update, name="user-update"),
]
