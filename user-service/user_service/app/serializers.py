from rest_framework import serializers
from .models import ManagerNote, StaffAction, UserAccount


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }


class StaffActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAction
        fields = "__all__"


class ManagerNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerNote
        fields = "__all__"