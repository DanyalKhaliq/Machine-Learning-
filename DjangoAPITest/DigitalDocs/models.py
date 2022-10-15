from django.db import models

# Create your models here.


class Folders(models.Model):
    FolderId = models.AutoField(primary_key=True)
    FolderName = models.CharField(max_length=500)
    ParentFolderId = models.IntegerField(null=True)


class Topics(models.Model):
    TopicId = models.AutoField(primary_key=True)
    TopicName = models.CharField(max_length=500)
    Folder = models.ForeignKey(Folders, on_delete=models.CASCADE)


class Documents(models.Model):
    DocId = models.AutoField(primary_key=True)
    DocName = models.CharField(max_length=500)
    Topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
