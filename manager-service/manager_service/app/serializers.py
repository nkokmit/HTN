from rest_framework import serializers
from .models import ManagerNote


class ManagerNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerNote
        fields = "__all__"
from .models import *

class ManagerNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerNote
        fields = '__all__'
