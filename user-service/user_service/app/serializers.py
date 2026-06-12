from rest_framework import serializers
from .models import ManagerNote, StaffAction, UserAccount,UserAddress


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'name', 'email', 'phone', 'role']
        read_only_fields = ['email', 'role']  # Giữ nguyên Email và Role không cho sửa từ ProfileAccount


class StaffActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAction
        fields = "__all__"


class ManagerNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerNote
        fields = "__all__"

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'full_name', 'phone_number', 'city', 'district', 'ward', 'detail_address', 'is_default']
        read_only_fields = ['user'] # User được lấy tự động từ Session/Token khi tạo đơn