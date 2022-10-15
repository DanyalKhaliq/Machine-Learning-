from django.test import TestCase

# Create your tests here.
from .models import Folders, Documents, Topics


class FoldersTestCase(TestCase):
    def setUp(self):
        Folders.objects.create(FolderName="CustomerFeedback")
        Folders.objects.create(FolderName="Suggestions")

    def test_folders_with_name(self):
        """Folders that are made with names are correctly get back"""
        csfeedback = Folders.objects.get(FolderName="CustomerFeedback")
        suggest = Folders.objects.get(FolderName="Suggestions")
        self.assertEqual(csfeedback.FolderName, "CustomerFeedback")
        self.assertEqual(suggest.FolderName, "Suggestions")


class TopicsTestCase(TestCase):
    def setUp(self):
        Folders.objects.create(FolderName="CustomerFeedback")
        Folders.objects.create(FolderName="Suggestions")

        Topics.objects.create(TopicName="Cricket", Folder_id=1)
        Topics.objects.create(TopicName="Politics", Folder_id=2)

    def test_topics_with_name(self):
        """Topics that are made with names are correctly get back"""
        cktTopic = Topics.objects.get(TopicName="Cricket")
        pltTopic = Topics.objects.get(TopicName="Politics")
        self.assertEqual(cktTopic.TopicName, "Cricket")
        self.assertEqual(pltTopic.TopicName, "Politics")


class DocumentsTestCase(TestCase):
    def setUp(self):
        Folders.objects.create(FolderName="CustomerFeedback")
        Folders.objects.create(FolderName="Suggestions")

        Topics.objects.create(TopicName="SpekiLove", Folder_id=1)
        Topics.objects.create(TopicName="Cricket", Folder_id=2)
        Topics.objects.create(TopicName="Politics", Folder_id=2)

        Documents.objects.create(DocName="Doc #1", Topic_id=1)
        Documents.objects.create(DocName="Doc #2", Topic_id=1)
        Documents.objects.create(DocName="Doc #3", Topic_id=2)

    def test_documents_length(self):
        """Documents length for specific topic"""

        cktTopic = Topics.objects.get(TopicName="SpekiLove")

        topics_filtered = Topics.objects.get(TopicId=cktTopic.TopicId)

        docs = topics_filtered.documents_set.all()

        self.assertEqual(cktTopic.TopicName, "SpekiLove")
        self.assertEqual(len(docs), 2)
