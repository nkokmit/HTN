from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentCreate(APIView):
    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'ship-service'})
