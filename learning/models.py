import re
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from googleapiclient.discovery import build


def get_video_id(url: str) -> str | None:
    """
    Extracts YouTube video ID from various URL formats.
    """
    # https://stackoverflow.com/a/7936523/12314699
    regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=)?(?:embed/)?(?:v/)?(?:shorts/)?(?P<video_id>[\w-]{11})"
    match = re.search(regex, url)
    return match.group("video_id") if match else None


def fetch_video_data(video_id: str) -> dict:
    """
    Fetches video title, description, and thumbnail URL from the YouTube API.
    """
    api_key = getattr(settings, "YOUTUBE_API_KEY", None)
    if not api_key:
        print("⚠️ YouTube API key not configured. Skipping video data fetch.")
        return {}

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()

        if items := response.get("items"):
            snippet = items[0].get("snippet", {})
            thumbnails = snippet.get("thumbnails", {})
            return {
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "thumbnail_url": (
                    thumbnails.get("high", {}).get("url")
                    or thumbnails.get("medium", {}).get("url")
                    or thumbnails.get("default", {}).get("url")
                ),
            }
    except Exception as e:
        print(f"❌ Error fetching YouTube API data for video ID {video_id}: {e}")

    return {}



class Link(models.Model):
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name="links")
    url = models.URLField(max_length=2048)
    video_id = models.CharField(max_length=20, blank=True, editable=False)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=2048, blank=True)

    def __str__(self):
        return self.title or self.url

    def save(self, *args, **kwargs):
        # Process only on creation and if the URL is a YouTube URL
        if "youtube.com" in self.url or "youtu.be" in self.url:
            video_id = get_video_id(self.url)
            if video_id:
                self.video_id = video_id
                data = fetch_video_data(video_id)
                self.title = data.get("title", "Untitled Video")
                description = data.get("description", "No description available.")
                self.description = (description.split('. ')[0] + '.') if '. ' in description else description
                self.thumbnail_url = data.get(
                    "thumbnail_url", f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                )
        super().save(*args, **kwargs)


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
