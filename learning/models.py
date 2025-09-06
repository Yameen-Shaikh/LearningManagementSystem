from django.db import models
from django.contrib.auth.models import User
import re
import requests
from urllib.parse import urlsplit

def get_video_id(url):
    video_id = None
    if 'youtu.be' in url:
        path = urlsplit(url).path
        video_id = path.split('/')[-1]
    else:
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11}).*', url)
        if match:
            video_id = match.group(1)
    return video_id

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

    def save(self, *args, **kwargs):
        video_id = get_video_id(self.url)
        if video_id:
            self.video_id = video_id
            try:
                oembed_url = f'https://www.youtube.com/oembed?url={self.url}&format=json'
                response = requests.get(oembed_url)
                response.raise_for_status() # Raise an exception for HTTP errors
                data = response.json()
                self.title = data.get('title', 'Unknown Title')
                self.thumbnail_url = data.get('thumbnail_url')
                # oEmbed for YouTube doesn't provide a clean description.
                # The 'html' field contains the full embed code.
                # We could try to parse it, but for now, we'll leave the description empty.
                self.description = data.get('author_name') # Using author name as description for now
            except requests.exceptions.RequestException as e:
                print(f'Error fetching video title: {e}')
            except Exception as e:
                print(f'Error adding video: {e}')
        super().save(*args, **kwargs)