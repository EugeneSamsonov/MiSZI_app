from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.control_panel, name="control-panel"),
    path(r"tests-list", views.tests_list, name="list"),
    path(r"", views.control_panel, name="test-update"),
    path(r"create-test", views.create_test, name="create-test"),
    path(r"delete-test/<int:test_id>", views.delete_test, name="test-delete"),
    path(r"test-attempt/<int:test_id>", views.test, name="test-attempt"),
    # path(r"create-test", views.create_test, name="test-update"),
]
