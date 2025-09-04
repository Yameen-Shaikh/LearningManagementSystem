from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

class Topic(models.Model):
    name = models.CharField(max_length=100)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"

class Link(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

    def __str__(self):
        return f"Link for {self.topic.name}"