from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

BOOK_SERVICE_URL = 'http://book-service:8000'


class CatalogView(APIView):
    def get(self, request):
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        if r.status_code != 200:
            return Response({'error': 'Book service unavailable'}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(r.json())


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'catalog-service'})
