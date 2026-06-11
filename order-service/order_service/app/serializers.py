from decimal import Decimal

from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product_id', 'product_type', 'title', 'quantity', 'unit_price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_id',
            'total_amount',
            'pay_method',
            'ship_method',
            'status',
            'shipping_address',
            'shipping_phone',
            'shipping_city',
            'note',
            'items',
        ]


class OrderCreateSerializer(serializers.Serializer):
    ALLOWED_PAY_METHODS = {"COD", "CARD", "BANK"}
    ALLOWED_SHIP_METHODS = {"FAST", "STANDARD", "EXPRESS"}

    customer_id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pay_method = serializers.CharField(required=False, default='COD')
    ship_method = serializers.CharField(required=False, default='STANDARD')
    status = serializers.CharField(required=False, default='CREATED')
    shipping_address = serializers.CharField(max_length=500)
    shipping_phone = serializers.CharField(max_length=20)
    shipping_city = serializers.CharField(max_length=100)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=1, default=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    product_type = serializers.CharField(required=False, default='BOOK')
    title = serializers.CharField(required=False, allow_blank=True, default='')
    order_items = serializers.ListField(child=serializers.DictField(), required=False)

    def validate_pay_method(self, value):
        normalized = str(value).upper()
        if normalized not in self.ALLOWED_PAY_METHODS:
            raise serializers.ValidationError("pay_method must be one of COD, CARD, BANK")
        return normalized

    def validate_ship_method(self, value):
        normalized = str(value).upper()
        if normalized not in self.ALLOWED_SHIP_METHODS:
            raise serializers.ValidationError("ship_method must be one of FAST, STANDARD, EXPRESS")
        return normalized

    def validate(self, attrs):
        order_items = attrs.get('order_items') or []
        if order_items:
            return attrs

        if attrs.get('product_id') is None:
            raise serializers.ValidationError({'product_id': 'product_id is required when order_items is not provided'})

        if attrs.get('unit_price') is None:
            raise serializers.ValidationError({'unit_price': 'unit_price is required when product_id is provided'})

        return attrs

    def get_order_items(self, validated_data):
        order_items = validated_data.get('order_items') or []
        if order_items:
            return order_items

        return [{
            'product_id': validated_data['product_id'],
            'product_type': validated_data.get('product_type', 'BOOK'),
            'title': validated_data.get('title', ''),
            'quantity': validated_data.get('quantity', 1),
            'unit_price': validated_data['unit_price'],
        }]

    def build_subtotal(self, unit_price, quantity):
        return Decimal(str(unit_price)) * Decimal(str(quantity))
