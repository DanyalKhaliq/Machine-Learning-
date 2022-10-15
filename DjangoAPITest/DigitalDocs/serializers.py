from rest_framework import serializers
from DigitalDocs.models import Folders, Documents, Topics


class FoldersSerializers(serializers.ModelSerializer):
    class Meta:
        model = Folders
        fields = ("FolderId", "FolderName", "ParentFolderId")


class TopicsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Topics
        fields = ("TopicId", "TopicName", "Folder_id")


class DocumentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ("DocId", "DocName", "Topic_id")
