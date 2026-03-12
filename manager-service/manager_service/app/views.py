from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ManagerNote
from .serializers import ManagerNoteSerializer


class ManagerNoteListCreate(APIView):
    def get(self, request):
        serializer = ManagerNoteSerializer(ManagerNote.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManagerNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'manager-service'})
