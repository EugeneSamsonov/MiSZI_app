from django.urls import path
from . import views

urlpatterns = [
    path(r"update-user", views.user_update, name="user-update"),
]
