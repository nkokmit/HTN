from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Rating
from .serializers import RatingSerializer
import requests


BOOK_SERVICE_URL = 'http://book-service:8000'


class RatingListCreate(APIView):
    def get(self, request):
        serializer = RatingSerializer(Rating.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        score = request.data.get('score')
        try:
            score = int(score)
        except (TypeError, ValueError):
            return Response({'error': 'score must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        if score < 1 or score > 5:
            return Response({'error': 'score must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'error': 'book_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        r = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
        if r.status_code != 200:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'comment-rate-service'})
