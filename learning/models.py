import re
from django.db import models
from django.contrib.auth.models import User
import requests
from urllib.parse import urlsplit
from django.core.exceptions import ValidationError

def get_video_id(url: str):
    """
    Extracts YouTube video ID from different YouTube URL formats.
    Supports: normal videos, shorts, embed, etc.
    """
    regex_patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # watch?v=, embed/, etc.
        r'youtu\.be\/([0-9A-Za-z_-]{11})',  # youtu.be short links
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

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
    video_id = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Link for {self.topic.name}"

    def clean(self):
        if self.url:
            video_id = get_video_id(self.url)
            if video_id:
                self.video_id = video_id
                try:
                    oembed_url = f'https://www.youtube.com/oembed?url={self.url}&format=json'
                    response = requests.get(oembed_url)
                    response.raise_for_status()
                    data = response.json()

                    self.title = data.get('title')
                    self.thumbnail_url = data.get('thumbnail_url')
                    self.description = data.get('author_name')

                    if not self.title or not self.thumbnail_url:
                        raise ValidationError(f"Could not retrieve essential oEmbed data for {self.url}. The video may be private or deleted.")

                except requests.exceptions.RequestException as e:
                    raise ValidationError(f'Error fetching oEmbed data for {self.url}: {e}') from e
            else:
                raise ValidationError("Could not extract video ID from the URL. Please use a valid YouTube URL.")

    def save(self, *args, **kwargs):
        # The admin calls full_clean() before save, so our clean() method will be run.
        super().save(*args, **kwargs)
