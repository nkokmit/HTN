from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from decimal import Decimal
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderSerializer

PAY_SERVICE_URL = 'http://pay-service:8000'
SHIP_SERVICE_URL = 'http://ship-service:8000'

def _safe_json_parse(response):
    """Hàm bọc an toàn để tránh sập server nếu service khác trả về HTML thay vì JSON"""
    try:
        return response.json() if response.content else {}
    except Exception:
        return {"error": "Invalid JSON returned from service", "status": response.status_code}

class OrderListCreate(APIView):
    def get(self, request):
        queryset = Order.objects.all().order_by('-id')
        customer_id = request.query_params.get('customer_id')
        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        order = Order.objects.create(
            customer_id=data['customer_id'],
            status=data.get('status', 'CREATED'),
            total_amount=data['total_amount'],
            pay_method=data.get('pay_method', 'COD'),
            ship_method=data.get('ship_method', 'STANDARD'),
            shipping_address=data['shipping_address'],
            shipping_phone=data['shipping_phone'],
            shipping_city=data['shipping_city'],
            note=data.get('note', '') or '',
        )

        order_items = serializer.get_order_items(data)
        for item in order_items:
            try:
                product_id = item.get('product_id')
                if product_id is None:
                    continue

                quantity = int(item.get('quantity', 1))
                unit_price = Decimal(str(item.get('unit_price', 0)))
                product_type = item.get('product_type', 'BOOK')

                OrderItem.objects.create(
                    order=order,
                    product_id=int(product_id),
                    product_type=product_type,
                    title=item.get('title', ''),
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=unit_price * Decimal(str(quantity)),
                )
            except Exception as e:
                print(f"Error creating order item: {e}")
                continue

        payment_payload = {
            'order_id': order.id,
            'method': data.get('pay_method', 'COD'),
            'amount': str(order.total_amount),
        }
        shipment_payload = {
            'order_id': order.id,
            'method': data.get('ship_method', 'STANDARD'),
            'address': data['shipping_address'],
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

        # Áp dụng hàm _safe_json_parse ở đây
        return Response(
            {
                'order': OrderSerializer(order).data,
                'payment': _safe_json_parse(pay_resp),
                'shipment': _safe_json_parse(ship_resp),
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