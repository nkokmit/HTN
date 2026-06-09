from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Product.objects.select_related(
        "category",
        "book",
        "electronics",
        "fashion",
        "home",
        "toy",
        "health",
    ).all().order_by("id")
    serializer_class = ProductSerializer


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "catalog-service", "domain": "product"})
