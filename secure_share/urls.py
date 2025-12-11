from django.urls import path
from secure_share import views

urlpatterns = [
    path(r"", views.HomeView.as_view(), name="home"),
    path(r"file-links/<uuid:file_name>", views.FileLinksView.as_view(), name="file_links"),
    path("download/<uuid:token>/", views.DownloadFileView.as_view(), name="download"),
    path("delete-file/", views.DeleteFileView.as_view(), name="delete_file"),
    path("delete-link/", views.DeleteFileLinkView.as_view(), name="delete_link"),
]
