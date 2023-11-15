from django.shortcuts import render
from rest_framework import viewsets
from .serializers import FictionFountainSerializer
from .models import FictionFountain
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.middleware.csrf import get_token


# Create your views here.

class FictionFountainView(viewsets.ModelViewSet):
    serializer_class = FictionFountainSerializer
    queryset = FictionFountain.objects.all()
    
    @action(detail=True, methods=['post'])
    def generate_settings(self, request, pk=None):
        print('increase_reading_progress called')
        fiction_fountain = self.get_object()
        fiction_fountain.generate_settings()
        return Response({'generate_settings': fiction_fountain.generate_settings()}, status=status.HTTP_200_OK)
        
    
    @action(detail=True, methods=['post'])
    def increase_reading_progress(self, request, pk=None):
        print('increase_reading_progress called')
        fiction_fountain = self.get_object()
        fiction_fountain.reading_progress += 1
        fiction_fountain.save()
        print(f'{fiction_fountain.reading_progress} {fiction_fountain.next_chapter_id-1}')
        return Response({'reading_progress': fiction_fountain.reading_progress}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def check_reading_progress(self, reqquest, pk=None):
        fiction_fountain = self.get_object()
        generated_chapter = fiction_fountain.generate_chapter()
        return Response({'generate_chapter': generated_chapter}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reset_reading_progress(self, request, pk=None):
        fiction_fountain = self.get_object()
        fiction_fountain.reading_progress = 0
        fiction_fountain.save()
        return Response({'reading_progress': fiction_fountain.reading_progress}, status=status.HTTP_200_OK)

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})