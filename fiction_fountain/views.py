from django.shortcuts import render
from rest_framework import viewsets
from .serializers import FictionFountainSerializer
from .models import FictionFountain
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.

class FictionFountainView(viewsets.ModelViewSet):
    serializer_class = FictionFountainSerializer
    queryset = FictionFountain.objects.all()
    
    @action(detail=True, methods=['post'])
    def increase_reading_progress(self, request, pk=None):
        fiction_fountain = self.get_object()
        fiction_fountain.reading_progress += 1
        fiction_fountain.save()
        if fiction_fountain.reading_progress == fiction_fountain.next_chapter_id-1:
            fiction_fountain.generate_chapter()
        return Response({'reading_progress': fiction_fountain.reading_progress}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reset_reading_progress(self, request, pk=None):
        fiction_fountain = self.get_object()
        fiction_fountain.reading_progress = 0
        fiction_fountain.save()
        return Response({'reading_progress': fiction_fountain.reading_progress}, status=status.HTTP_200_OK)

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})