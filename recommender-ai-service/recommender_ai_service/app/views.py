from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

BOOK_SERVICE_URL = 'http://book-service:8000'
RATE_SERVICE_URL = 'http://comment-rate-service:8000'


class RecommendationView(APIView):
    def get(self, request):
        books_resp = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        ratings_resp = requests.get(f"{RATE_SERVICE_URL}/ratings/", timeout=5)
        if books_resp.status_code != 200 or ratings_resp.status_code != 200:
            return Response({'error': 'Dependencies unavailable'}, status=status.HTTP_502_BAD_GATEWAY)

        books = books_resp.json()
        ratings = ratings_resp.json()

        score_map = {}
        count_map = {}
        for item in ratings:
            book_id = item.get('book_id')
            score = item.get('score', 0)
            score_map[book_id] = score_map.get(book_id, 0) + score
            count_map[book_id] = count_map.get(book_id, 0) + 1

        for b in books:
            bid = b.get('id')
            if count_map.get(bid):
                b['avg_score'] = score_map[bid] / count_map[bid]
            else:
                b['avg_score'] = 0

        books.sort(key=lambda x: x.get('avg_score', 0), reverse=True)
        return Response({'recommendations': books[:5]})


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'recommender-ai-service'})
