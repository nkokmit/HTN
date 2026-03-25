from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Clothes, ClothesVariant
from .serializers import (
    ClothesListSerializer,
    ClothesDetailSerializer,
    ClothesCreateUpdateSerializer,
    ClothesVariantSerializer,
    ClothesVariantCreateUpdateSerializer,
)


class ClothesListView(APIView):
    """List all clothes and create new clothes"""

    def get(self, request):
        """Get all clothes"""
        clothes = Clothes.objects.all()
        serializer = ClothesListSerializer(clothes, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new clothes (staff only)"""
        serializer = ClothesCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            clothes = serializer.save()
            return Response(
                ClothesDetailSerializer(clothes).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClothesDetailView(APIView):
    """Get, update, or delete specific clothes"""

    def get(self, request, pk):
        """Get clothes detail with variants"""
        try:
            clothes = Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesDetailSerializer(clothes)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update clothes (staff only)"""
        try:
            clothes = Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesCreateUpdateSerializer(clothes, data=request.data)
        if serializer.is_valid():
            clothes = serializer.save()
            return Response(ClothesDetailSerializer(clothes).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete clothes (staff only)"""
        try:
            clothes = Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        clothes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClothesVariantListView(APIView):
    """List variants for a clothes and create new variant"""

    def get(self, request, clothes_id):
        """Get all variants for a clothes"""
        try:
            clothes = Clothes.objects.get(pk=clothes_id)
        except Clothes.DoesNotExist:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        variants = clothes.variants.all()
        serializer = ClothesVariantSerializer(variants, many=True)
        return Response(serializer.data)

    def post(self, request, clothes_id):
        """Create new variant for clothes (staff only)"""
        try:
            clothes = Clothes.objects.get(pk=clothes_id)
        except Clothes.DoesNotExist:
            return Response(
                {"error": "Clothes not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesVariantCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            variant = serializer.save(clothes=clothes)
            return Response(
                ClothesVariantSerializer(variant).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClothesVariantDetailView(APIView):
    """Get, update, or delete specific variant"""

    def get(self, request, clothes_id, variant_id):
        """Get variant detail"""
        try:
            variant = ClothesVariant.objects.get(id=variant_id, clothes_id=clothes_id)
        except ClothesVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesVariantSerializer(variant)
        return Response(serializer.data)

    def put(self, request, clothes_id, variant_id):
        """Update variant (staff only)"""
        try:
            variant = ClothesVariant.objects.get(id=variant_id, clothes_id=clothes_id)
        except ClothesVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClothesVariantCreateUpdateSerializer(variant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(ClothesVariantSerializer(variant).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, clothes_id, variant_id):
        """Delete variant (staff only)"""
        try:
            variant = ClothesVariant.objects.get(id=variant_id, clothes_id=clothes_id)
        except ClothesVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
