from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from decimal import Decimal
from .models import Order, OrderItem
from .serializers import OrderSerializer

PAY_SERVICE_URL = 'http://pay-service:8000'
SHIP_SERVICE_URL = 'http://ship-service:8000'


class OrderListCreate(APIView):
    def get(self, request):
        queryset = Order.objects.all().order_by('-id')
        customer_id = request.query_params.get('customer_id')
        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()

        order_items = request.data.get('order_items', [])
        if isinstance(order_items, list):
            for item in order_items:
                try:
                    item_type = str(item.get('item_type', 'BOOK')).upper()
                    if item_type not in {'BOOK', 'CLOTHES'}:
                        item_type = 'BOOK'

                    raw_book_id = item.get('book_id')
                    raw_clothes_id = item.get('clothes_id')
                    raw_variant_id = item.get('clothes_variant_id')

                    OrderItem.objects.create(
                        order=order,
                        cart_item_id=item.get('cart_item_id'),
                        item_type=item_type,
                        book_id=int(raw_book_id) if raw_book_id is not None else None,
                        clothes_id=int(raw_clothes_id) if raw_clothes_id is not None else None,
                        clothes_variant_id=int(raw_variant_id) if raw_variant_id is not None else None,
                        size=item.get('size', None),
                        color=item.get('color', None),
                        title=item.get('title', ''),
                        unit_price=Decimal(str(item.get('unit_price', 0))),
                        quantity=int(item.get('quantity', 1)),
                        subtotal=Decimal(str(item.get('subtotal', 0))),
                    )
                except Exception:
                    continue

        payment_payload = {
            'order_id': order.id,
            'method': order.pay_method,
            'amount': str(order.total_amount),
        }
        shipment_payload = {
            'order_id': order.id,
            'method': order.ship_method,
        }

        try:
            pay_resp = requests.post(f"{PAY_SERVICE_URL}/payments/", json=payment_payload, timeout=5)
            ship_resp = requests.post(f"{SHIP_SERVICE_URL}/shipments/", json=shipment_payload, timeout=5)
        except requests.RequestException:
            order.status = 'DEPENDENCY_UNAVAILABLE'
            order.save()
            return Response(
                {'error': 'Payment or shipping service unavailable', 'order': OrderSerializer(order).data},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if pay_resp.status_code in (200, 201) and ship_resp.status_code in (200, 201):
            order.status = 'PAYMENT_AND_SHIPPING_CREATED'
        else:
            order.status = 'PARTIAL_FAILED'
        order.save()

        return Response(
            {
                'order': OrderSerializer(order).data,
                'payment': pay_resp.json() if pay_resp.content else {},
                'shipment': ship_resp.json() if ship_resp.content else {},
            },
            status=status.HTTP_201_CREATED,
        )


class OrderDetail(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'order-service'})
