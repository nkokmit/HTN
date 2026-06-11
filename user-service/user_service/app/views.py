from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import ManagerNote, UserAccount, UserRole
from .serializers import ManagerNoteSerializer, StaffActionSerializer, UserAccountSerializer

CART_SERVICE_URL = "http://cart-service:8000"
PRODUCT_SERVICE_URL = "http://product-service:8000"


def _normalize_role(role_value, default=UserRole.CUSTOMER):
    role = (role_value or default).upper()
    allowed_roles = {choice for choice, _ in UserRole.choices}
    if role not in allowed_roles:
        return None
    return role


def _create_customer_and_cart(payload):
    serializer = UserAccountSerializer(data=payload)
    if not serializer.is_valid():
        return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    if user.role != UserRole.CUSTOMER:
        return user, Response(UserAccountSerializer(user).data, status=status.HTTP_201_CREATED)

    try:
        cart_resp = requests.post(
            f"{CART_SERVICE_URL}/carts/",
            json={"customer_id": user.id},
            timeout=5,
        )
        if cart_resp.status_code not in (200, 201):
            user.delete()
            return None, Response(
                {"error": "Customer registration failed because cart creation failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
    except requests.RequestException:
        user.delete()
        return None, Response(
            {"error": "Customer registration failed because cart creation is unavailable"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return user, Response(UserAccountSerializer(user).data, status=status.HTTP_201_CREATED)


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "user-service"})


class UsersListCreate(APIView):
    def get(self, request):
        users = UserAccount.objects.all().order_by("id")
        serializer = UserAccountSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        role = _normalize_role(request.data.get("role"), default=UserRole.CUSTOMER)
        if not role:
            return Response({"error": "role must be one of ADMIN, STAFF, CUSTOMER"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "password": request.data.get("password", "123456"),
            "role": role,
        }
        _, response = _create_customer_and_cart(payload)
        return response

class CustomerListCreate(APIView):
    def get(self, request):
        customers = UserAccount.objects.filter(role=UserRole.CUSTOMER).order_by("id")
        serializer = UserAccountSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        payload = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "password": request.data.get("password", "123456"),
            "role": UserRole.CUSTOMER,
        }
        _, response = _create_customer_and_cart(payload)
        return response


class RegisterView(APIView):
    def post(self, request):
        role = _normalize_role(request.data.get("role"), default=UserRole.CUSTOMER)
        if not role:
            return Response({"error": "role must be one of ADMIN, STAFF, CUSTOMER"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "password": request.data.get("password"),
            "role": role,
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
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.password != password:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "token": f"demo-token-{user.id}",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role,
                },
            }
        )


class UserDetailUpdateView(APIView):
    def get(self, request, user_id):
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserAccountSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserAccountSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserAccountSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffBookManageView(APIView):
    def get(self, request):
        r = requests.get(f"{PRODUCT_SERVICE_URL}/products/", timeout=5)
        if r.status_code != 200:
            return Response({"error": "Cannot fetch books"}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(r.json())

    def post(self, request):
        payload = request.data.get("book", {})
        r = requests.post(f"{PRODUCT_SERVICE_URL}/products/", json=payload, timeout=5)
        if r.status_code not in (200, 201):
            return Response({"error": "Cannot create book"}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(
            data={
                "product_id": r.json().get("id"),
                "action": "create",
                "note": request.data.get("note", ""),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"book": r.json(), "action": serializer.data}, status=status.HTTP_201_CREATED)


class StaffBookManageDetailView(APIView):
    def get(self, request, product_id):
        r = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", timeout=5)
        if r.status_code == 404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        if r.status_code != 200:
            return Response({"error": "Cannot fetch product", "details": r.text}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(r.json())

    def patch(self, request, product_id):
        r = requests.patch(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", json=request.data, timeout=5)
        if r.status_code == 404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        if r.status_code != 200:
            return Response({"error": "Cannot update product", "details": r.text}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(data={"product_id": product_id, "action": "update", "note": request.data.get("note", "")})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"product": r.json(), "action": serializer.data})

    def delete(self, request, product_id):
        r = requests.delete(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", timeout=5)
        if r.status_code == 404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        if r.status_code != 204:
            return Response({"error": "Cannot delete product", "details": r.text}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(data={"product_id": product_id, "action": "delete", "note": request.data.get("note", "") if isinstance(request.data, dict) else ""})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Product deleted", "action": serializer.data})


class ManagerNoteListCreate(APIView):
    def get(self, request):
        serializer = ManagerNoteSerializer(ManagerNote.objects.all().order_by("id"), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManagerNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
