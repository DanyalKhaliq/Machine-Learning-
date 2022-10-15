from pickle import NONE
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from DigitalDocs.models import Folders, Documents, Topics
from DigitalDocs.serializers import (
    FoldersSerializers,
    TopicsSerializers,
    DocumentsSerializers,
)

# Create your views here.


@csrf_exempt
def FolderApi(request, Id=0):
    if request.method == "GET":

        query_folder = request.GET.get("foldername")
        query_topic = request.GET.get("topicname")

        if query_folder is not None and query_topic is not None:
            return returnQuerySearchResults(
                FolderName=query_folder, TopicName=query_topic
            )

        folders = Folders.objects.all()
        folders_serializer = FoldersSerializers(folders, many=True)
        return JsonResponse(folders_serializer.data, safe=False)

    elif request.method == "POST":
        folders_data = JSONParser().parse(request)
        folders_serializer = FoldersSerializers(data=folders_data)
        if folders_serializer.is_valid():
            folders_serializer.save()
            return JsonResponse("Added Folder Successfully !", safe=False)
        return JsonResponse("Failed to add Folder !", safe=False)

    elif request.method == "PUT":
        folders_data = JSONParser().parse(request)
        folder = Folders.objects.get(FolderId=folders_data["FolderId"])
        folders_serializer = FoldersSerializers(folder, data=folders_data)
        if folders_serializer.is_valid():
            folders_serializer.save()
            return JsonResponse("Updated Folder Successfully !", safe=False)
        return JsonResponse("Failed to add Folder !", safe=False)

    elif request.method == "DELETE":
        folder = Folders.objects.get(FolderId=Id)
        folder.delete()
        return JsonResponse("Deleted the Folder Successfully !", safe=False)


def returnQuerySearchResults(FolderName="CustomerFeedback", TopicName="Spekilove"):

    folder_data = Folders.objects.filter(FolderName=FolderName).values()

    if folder_data is not None and len(folder_data) > 0:

        topic_data = Topics.objects.filter(
            TopicName=TopicName, Folder_id=folder_data[0]["FolderId"]
        ).values()

        if topic_data is not None and len(topic_data) > 0:

            topics_filtered = Topics.objects.get(TopicId=topic_data[0]["TopicId"])

            docs = topics_filtered.documents_set.all()

            topics_serializer = DocumentsSerializers(docs, many=True)

            return JsonResponse(topics_serializer.data, safe=False)

        return JsonResponse("Failed to load Topic !", safe=False)
    return JsonResponse("Failed to load Folder !", safe=False)


@csrf_exempt
def TopicApi(request, Id=0):
    if request.method == "GET":
        topics = Topics.objects.all()
        topics_serializer = TopicsSerializers(topics, many=True)
        return JsonResponse(topics_serializer.data, safe=False)

    elif request.method == "POST":
        topics_data = JSONParser().parse(request)
        topics_serializer = TopicsSerializers(data=topics_data)
        if topics_serializer.is_valid():
            topics_serializer.save()
            return JsonResponse("Added Topic Successfully !", safe=False)
        return JsonResponse("Failed to add Topic !", safe=False)

    elif request.method == "PUT":
        topics_data = JSONParser().parse(request)
        topic = Topics.objects.get(TopicId=topics_data["TopicId"])
        topics_serializer = TopicsSerializers(topic, data=topics_data)
        if topics_serializer.is_valid():
            topics_serializer.save()
            return JsonResponse("Updated Topic Successfully !", safe=False)
        return JsonResponse("Failed to add Topic !", safe=False)

    elif request.method == "DELETE":
        topic = Topics.objects.get(TopicId=Id)
        topic.delete()
        return JsonResponse("Deleted the Topic Successfully !", safe=False)


@csrf_exempt
def DocumentApi(request, Id=0):
    if request.method == "GET":
        documents = Documents.objects.all()
        documents_serializer = DocumentsSerializers(documents, many=True)
        return JsonResponse(documents_serializer.data, safe=False)

    elif request.method == "POST":
        documents_data = JSONParser().parse(request)
        documents_serializer = DocumentsSerializers(data=documents_data)
        if documents_serializer.is_valid():
            documents_serializer.save()
            return JsonResponse("Added Doc Successfully !", safe=False)
        return JsonResponse("Failed to add Doc !", safe=False)

    elif request.method == "PUT":
        documents_data = JSONParser().parse(request)
        document = Documents.objects.get(DocId=documents_data["DocId"])
        documents_serializer = DocumentsSerializers(document, data=documents_data)
        if documents_serializer.is_valid():
            documents_serializer.save()
            return JsonResponse("Updated Doc Successfully !", safe=False)
        return JsonResponse("Failed to add Doc !", safe=False)

    elif request.method == "DELETE":
        document = Documents.objects.get(DocId=Id)
        document.delete()
        return JsonResponse("Deleted the Doc Successfully !", safe=False)
