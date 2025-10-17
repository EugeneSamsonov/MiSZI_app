from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.control_panel, name="control-panel"),
    path(r"home", views.home, name="home"),
    path(r"", views.control_panel, name="test-update"),
    path(r"create-test", views.create_test, name="create-test"),
    path(r"delete-test/<int:test_id>", views.delete_test, name="test-delete"),
    # path(r"create-test", views.create_test, name="test-update"),
]
