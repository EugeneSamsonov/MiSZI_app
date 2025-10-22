from django.urls import path
from . import views

urlpatterns = [
    path(r"", views.home, name="home"),
    path(r"tests-list", views.tests_list, name="list"),
    path(r"control-panel", views.control_panel, name="control-panel"),
    path(r"create-test", views.create_test, name="create-test"),
    path(r"delete-test/<int:test_id>", views.delete_test, name="test-delete"),
    path(r"test-attempt/<int:test_id>", views.test, name="test-attempt"),
    path(r"attempt-result/<int:test_id>", views.attempt_result, name="attempt-result"),
]
