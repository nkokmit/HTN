from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentCreate(APIView):
    """
    Create a new shipment for an order
    POST /shipments/ - Create shipment
    """
    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipment = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShipmentDetail(APIView):
    """
    Retrieve, update, or delete a specific shipment
    GET /shipments/<id>/ - Get shipment details and status
    PUT /shipments/<id>/ - Update shipment status
    """
    def get(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShipmentStatusView(APIView):
    """
    Check shipment status by order_id
    GET /shipments/order/<order_id>/ - Get status by order ID
    """
    def get(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            serializer = ShipmentSerializer(shipment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Shipment.DoesNotExist:
            return Response(
                {'detail': f'Shipment for order {order_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'ship-service'})
