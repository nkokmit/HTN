from rest_framework import serializers
from .models import *


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    ALLOWED_PAY_METHODS = {"COD", "CARD", "BANK"}
    ALLOWED_SHIP_METHODS = {"FAST", "STANDARD", "EXPRESS"}
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def validate_pay_method(self, value):
        if value not in self.ALLOWED_PAY_METHODS:
            raise serializers.ValidationError("pay_method must be one of COD, CARD, BANK")
        return value

    def validate_ship_method(self, value):
        if value not in self.ALLOWED_SHIP_METHODS:
            raise serializers.ValidationError("ship_method must be one of FAST, STANDARD, EXPRESS")
        return value
