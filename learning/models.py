import re
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from googleapiclient.discovery import build


def get_video_id(url: str):
    """
    Extracts YouTube video ID from different YouTube URL formats.
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


def fetch_video_data(video_id):
    api_key = os.environ.get("YOUTUBE_API_KEY") or getattr(settings, "YOUTUBE_API_KEY", None)
    if not api_key:
        print("⚠️ No YouTube API key configured.")
        return {}

    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()

    if response.get("items"):
        snippet = response["items"][0]["snippet"]
        thumbnails = snippet.get("thumbnails", {})
        return {
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "thumbnail_url": (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("default", {}).get("url")
            ),
        }
    return {}


class Link(models.Model):
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name="links")
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
                    data = fetch_video_data(video_id)
                    self.title = data.get("title")
                    self.description = data.get("description")
                    self.thumbnail_url = data.get("thumbnail_url")
                except Exception as e:
                    print(f"Error fetching YouTube API data for {self.url}: {e}")
                    pass
            else:
                raise ValidationError(
                    "Could not extract video ID from the URL. Please use a valid YouTube URL."
                )


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
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"
