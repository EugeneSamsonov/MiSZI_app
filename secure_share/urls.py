from django.urls import path
from secure_share import views

urlpatterns = [
    path(r"", views.HomeView.as_view(), name="home"),
    path(r"file_links/<uuid:file_name>", views.FileLinksView.as_view(), name="file_links"),
    path("download/<uuid:token>/", views.DownloadFileView.as_view(), name="download"),

    # path(r"control-panel/<str:category>", views.control_panel, name="control-panel"),

    # path(r"tests-list", views.tests_list, name="list"),
    # path(r"tests-list/<str:category>", views.tests_list, name="list"),

    # path(r"list-passed-users/<str:category>", views.list_passed_users, name="list-passed-users"),
    # path(r"list-passed-users/<str:category>/<int:test_id>", views.list_passed_users, name="list-passed-users"),

    # path(r"create-test/<str:category>", views.create_test, name="create-test"),
    # path(r"delete-test/<int:test_id>", views.delete_test, name="test-delete"),

    # path(r"test-attempt/<int:test_id>", views.test, name="test-attempt"),
    # path(r"attempt-result/<int:test_id>", views.attempt_result, name="attempt-result"),
]
