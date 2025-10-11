from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.control_panel, name="control-panel"),
    path(r"create-test", views.create_test, name="create-test"),
]
