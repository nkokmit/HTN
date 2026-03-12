from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"


def _create_customer_and_cart(payload):
    serializer = CustomerSerializer(data=payload)
    if not serializer.is_valid():
        return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer = serializer.save()

    try:
        cart_resp = requests.post(
            f"{CART_SERVICE_URL}/carts/",
            json={"customer_id": customer.id},
            timeout=5,
        )
        if cart_resp.status_code not in (200, 201):
            customer.delete()
            return None, Response(
                {"error": "Customer registration failed because cart creation failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
    except requests.RequestException:
        customer.delete()
        return None, Response(
            {"error": "Customer registration failed because cart creation is unavailable"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return customer, Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        payload = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "password": request.data.get("password", "123456"),
            "role": request.data.get("role", "CUSTOMER").upper(),
        }
        _, response = _create_customer_and_cart(payload)
        return response


class RegisterView(APIView):
    def post(self, request):
        payload = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "password": request.data.get("password"),
            "role": request.data.get("role", "CUSTOMER").upper(),
        }
        if not payload["password"]:
            return Response({"error": "password is required"}, status=status.HTTP_400_BAD_REQUEST)

        _, response = _create_customer_and_cart(payload)
        return response


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"error": "email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if customer.password != password:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "token": f"demo-token-{customer.id}",
                "user": {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "role": customer.role,
                },
            }
        )
