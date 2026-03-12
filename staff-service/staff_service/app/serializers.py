from rest_framework import serializers
from .models import StaffAction


class StaffActionSerializer(serializers.ModelSerializer):
	class Meta:
		model = StaffAction
		fields = "__all__"

