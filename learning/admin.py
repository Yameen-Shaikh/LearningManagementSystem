from django.contrib import admin
from .models import Subject, Chapter, Topic, Link

admin.site.register(Subject)
admin.site.register(Chapter)
admin.site.register(Topic)
admin.site.register(Link)