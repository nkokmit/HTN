from decimal import Decimal

import requests
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer

PRODUCT_SERVICE_URL = "http://product-service:8000"


def _fetch_product(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{int(product_id)}/", timeout=5)
    except (requests.RequestException, ValueError):
        return None, Response({"error": "Product service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if response.status_code == 404:
        return None, Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    if response.status_code != 200:
        return None, Response({"error": "Product service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return response.json(), None


class CartCreate(APIView):

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):

    @transaction.atomic
    def post(self, request):
        cart_id = request.data.get("cart")
        if not cart_id:
            return Response({"error": "cart is required"}, status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data.get("product_id") or request.data.get("book_id") or request.data.get("clothes_id")
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if quantity <= 0:
            return Response({"error": "quantity must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        product, error_response = _fetch_product(product_id)
        if error_response is not None:
            return error_response

        product_stock = int(product.get("stock", 0))
        if quantity > product_stock:
            return Response({"error": "quantity exceeds product stock"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "cart": cart_id,
            "product_id": int(product_id),
            "unit_price": Decimal(str(product.get("price", 0))),
            "quantity": quantity,
        }

        existing = CartItem.objects.filter(cart_id=cart_id, product_id=int(product_id)).first()

        if existing:
            new_quantity = existing.quantity + quantity
            if new_quantity > product_stock:
                return Response({"error": "quantity exceeds product stock"}, status=status.HTTP_400_BAD_REQUEST)
            existing.quantity = new_quantity
            existing.unit_price = payload["unit_price"]
            existing.save()
            return Response(CartItemSerializer(existing).data)

        serializer = CartItemSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCart(APIView):

    def get(self, request, customer_id):
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)

        items = CartItem.objects.filter(cart=cart).order_by("id")
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)


class CartByCustomer(APIView):
    def get(self, request, customer_id):
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class UpdateCartItem(APIView):
    def patch(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        new_quantity = request.data.get("quantity")
        if new_quantity is not None:
            try:
                new_quantity = int(new_quantity)
            except (TypeError, ValueError):
                return Response({"error": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            if new_quantity <= 0:
                return Response({"error": "quantity must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

            product, error_response = _fetch_product(item.product_id)
            if error_response is not None:
                return error_response
            if new_quantity > int(product.get("stock", 0)):
                return Response({"error": "quantity exceeds product stock"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)