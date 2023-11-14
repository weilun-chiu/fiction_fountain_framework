from django.contrib import admin
from .models import FictionFountain

class FictionFountainAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre', 'people', 'settings', 'outlines', 'chapters', 'reading_progress', 'next_chapter_id')

# Register your models here.

admin.site.register(FictionFountain, FictionFountainAdmin)
