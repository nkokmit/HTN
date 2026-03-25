from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CLOTHES_SERVICE_URL = "http://clothes-service:8000"


class CartCreate(APIView):

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):

    def post(self, request):
        item_type = str(request.data.get("item_type", "BOOK")).upper()
        if item_type not in {"BOOK", "CLOTHES"}:
            return Response({"error": "item_type must be BOOK or CLOTHES"}, status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.data.get("cart")
        if not cart_id:
            return Response({"error": "cart is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if quantity <= 0:
            return Response({"error": "quantity must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "cart": cart_id,
            "item_type": item_type,
            "quantity": quantity,
        }

        if item_type == "BOOK":
            book_id = request.data.get("book_id")
            if not book_id:
                return Response({"error": "book_id is required for BOOK"}, status=status.HTTP_400_BAD_REQUEST)

            r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
            if r.status_code != 200:
                return Response({"error": "Book service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            books = r.json()

            if not any(int(b["id"]) == int(book_id) for b in books):
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

            payload["book_id"] = int(book_id)
            existing = CartItem.objects.filter(cart_id=cart_id, item_type="BOOK", book_id=int(book_id)).first()
        else:
            clothes_id = request.data.get("clothes_id")
            size = str(request.data.get("size", "")).strip()
            color = str(request.data.get("color", "")).strip()
            if not clothes_id:
                return Response({"error": "clothes_id is required for CLOTHES"}, status=status.HTTP_400_BAD_REQUEST)
            if not size or not color:
                return Response({"error": "size and color are required for CLOTHES"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                variant_resp = requests.get(
                    f"{CLOTHES_SERVICE_URL}/clothes/{int(clothes_id)}/variants/",
                    timeout=5,
                )
            except requests.RequestException:
                return Response({"error": "Clothes service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            if variant_resp.status_code != 200:
                return Response({"error": "Clothes not found"}, status=status.HTTP_404_NOT_FOUND)

            variants = variant_resp.json()
            target_variant = None
            for variant in variants:
                if str(variant.get("size", "")).lower() == size.lower() and str(variant.get("color", "")).lower() == color.lower():
                    target_variant = variant
                    break

            if not target_variant:
                return Response({"error": "Variant not found for selected size/color"}, status=status.HTTP_404_NOT_FOUND)

            variant_stock = int(target_variant.get("stock", 0))
            if quantity > variant_stock:
                return Response({"error": "quantity exceeds variant stock"}, status=status.HTTP_400_BAD_REQUEST)

            payload.update({
                "clothes_id": int(clothes_id),
                "clothes_variant_id": int(target_variant.get("id")),
                "size": target_variant.get("size"),
                "color": target_variant.get("color"),
            })
            existing = CartItem.objects.filter(
                cart_id=cart_id,
                item_type="CLOTHES",
                clothes_variant_id=int(target_variant.get("id")),
            ).first()

        if existing:
            new_quantity = existing.quantity + quantity
            if item_type == "CLOTHES":
                if new_quantity > variant_stock:
                    return Response({"error": "quantity exceeds variant stock"}, status=status.HTTP_400_BAD_REQUEST)
            existing.quantity = new_quantity
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

        items = CartItem.objects.filter(cart=cart)
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