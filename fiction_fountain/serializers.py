from rest_framework import serializers
from .models import FictionFountain

class FictionFountainSerializer(serializers.ModelSerializer):
    class Meta:
        model = FictionFountain
        fields = ('id', 'genre', 'people', 'settings', 'outlines', 'chapters', 'reading_progress', 'next_chapter_id')
