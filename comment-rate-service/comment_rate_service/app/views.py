from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Rating
from .serializers import RatingSerializer
import requests


PRODUCT_SERVICE_URL = 'http://product-service:8000'
ORDER_SERVICE_URL = 'http://order-service:8000'


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

        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        r = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", timeout=5)
        if r.status_code != 200:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_resp = requests.get(f"{ORDER_SERVICE_URL}/orders/", params={'customer_id': customer_id}, timeout=5)
        except requests.RequestException:
            return Response({'error': 'Cannot validate purchase history'}, status=status.HTTP_502_BAD_GATEWAY)

        if order_resp.status_code != 200:
            return Response({'error': 'Cannot validate purchase history'}, status=status.HTTP_502_BAD_GATEWAY)

        purchased = False
        for order in order_resp.json():
            for item in order.get('items', []):
                item_prod_id = item.get('product_id') or item.get('book_id')
                if item_prod_id is None:
                    continue
                try:
                    if int(item_prod_id) == int(product_id):
                        purchased = True
                        break
                except (TypeError, ValueError):
                    continue
            if purchased:
                break

        if not purchased:
            return Response({'error': 'You can only rate books you have purchased'}, status=status.HTTP_400_BAD_REQUEST)

        # normalize incoming payload to product_id
        data = dict(request.data)
        if 'book_id' in data and 'product_id' not in data:
            data['product_id'] = data.get('book_id')
        serializer = RatingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'comment-rate-service'})
