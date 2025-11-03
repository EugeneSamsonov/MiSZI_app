from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.theory_list, name="list"),
    path(r"<str:category>", views.theory_list, name="list"),
    path(r"detail/<int:theory_id>", views.theory_detail, name="detail"),
]
