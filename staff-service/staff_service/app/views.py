from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import StaffActionSerializer


BOOK_SERVICE_URL = "http://book-service:8000"

class HealthView(APIView):
    def get(self, request):
        return Response({'status':'ok','service':'staff-service'})


class StaffBookManageView(APIView):
    def get(self, request):
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        if r.status_code != 200:
            return Response({"error": "Cannot fetch books"}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(r.json())

    def post(self, request):
        payload = request.data.get("book", {})
        r = requests.post(f"{BOOK_SERVICE_URL}/books/", json=payload, timeout=5)
        if r.status_code not in (200, 201):
            return Response({"error": "Cannot create book"}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(
            data={
                "book_id": r.json().get("id"),
                "action": "create",
                "note": request.data.get("note", ""),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"book": r.json(), "action": serializer.data}, status=status.HTTP_201_CREATED)


class StaffBookManageDetailView(APIView):
    def patch(self, request, book_id):
        r = requests.patch(f"{BOOK_SERVICE_URL}/books/{book_id}/", json=request.data, timeout=5)
        if r.status_code == 404:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        if r.status_code != 200:
            return Response({"error": "Cannot update book", "details": r.text}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(data={"book_id": book_id, "action": "update", "note": request.data.get("note", "")})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"book": r.json(), "action": serializer.data})

    def delete(self, request, book_id):
        r = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
        if r.status_code == 404:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        if r.status_code != 204:
            return Response({"error": "Cannot delete book", "details": r.text}, status=status.HTTP_502_BAD_GATEWAY)

        serializer = StaffActionSerializer(data={"book_id": book_id, "action": "delete", "note": request.data.get("note", "") if isinstance(request.data, dict) else ""})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Book deleted", "action": serializer.data})

