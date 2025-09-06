from django.contrib import admin
from .models import Subject, Chapter, Topic, Link

class LinkAdmin(admin.ModelAdmin):
    exclude = ('video_id', 'title', 'description', 'thumbnail_url')

admin.site.register(Subject)
admin.site.register(Chapter)
admin.site.register(Topic)
admin.site.register(Link, LinkAdmin)