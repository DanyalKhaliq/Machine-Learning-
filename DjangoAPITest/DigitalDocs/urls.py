from django.urls import path, re_path
from DigitalDocs import views


urlpatterns = [
    path("folders/", views.FolderApi),
    path("topics/", views.TopicApi),
    path("documents/", views.DocumentApi),
]
