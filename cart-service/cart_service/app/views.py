from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"


class CartCreate(APIView):

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):

    def post(self, request):
        book_id = request.data.get("book_id")
        if not book_id:
            return Response({"error": "book_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Gọi sang book-service để kiểm tra book tồn tại
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        if r.status_code != 200:
            return Response({"error": "Book service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        books = r.json()

        if not any(b["id"] == book_id for b in books):
            return Response(
                {"error": "Book not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_id = request.data.get("cart")
        if not cart_id:
            return Response({"error": "cart is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if quantity <= 0:
            return Response({"error": "quantity must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        existing = CartItem.objects.filter(cart_id=cart_id, book_id=book_id).first()
        if existing:
            existing.quantity += quantity
            existing.save()
            return Response(CartItemSerializer(existing).data)

        serializer = CartItemSerializer(data={"cart": cart_id, "book_id": book_id, "quantity": quantity})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCart(APIView):

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)


class CartByCustomer(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
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