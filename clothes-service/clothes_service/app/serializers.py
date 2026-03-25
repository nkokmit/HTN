from rest_framework import serializers
from .models import Clothes, ClothesVariant


class ClothesVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothesVariant
        fields = ['id', 'size', 'color', 'stock']


class ClothesListSerializer(serializers.ModelSerializer):
    """Serializer for clothes list view"""
    variants_count = serializers.SerializerMethodField()

    class Meta:
        model = Clothes
        fields = ['id', 'name', 'description', 'price', 'image_url', 'variants_count']

    def get_variants_count(self, obj):
        return obj.variants.count()


class ClothesDetailSerializer(serializers.ModelSerializer):
    """Serializer for clothes detail view with variants"""
    variants = ClothesVariantSerializer(many=True, read_only=True)
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Clothes
        fields = ['id', 'name', 'description', 'price', 'image_url', 'sizes', 'colors', 'variants', 'created_at', 'updated_at']

    def get_sizes(self, obj):
        return sorted({v.size for v in obj.variants.all()})

    def get_colors(self, obj):
        return sorted({v.color for v in obj.variants.all()})


class ClothesCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clothes"""
    sizes = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, write_only=True
    )
    colors = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, write_only=True
    )
    default_stock = serializers.IntegerField(required=False, min_value=0, write_only=True, default=0)

    class Meta:
        model = Clothes
        fields = ['name', 'description', 'price', 'image_url', 'sizes', 'colors', 'default_stock']

    @staticmethod
    def _normalize_values(values):
        normalized = []
        seen = set()
        for value in values:
            text = str(value).strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(text)
        return normalized

    def _sync_variants(self, clothes, sizes, colors, default_stock):
        desired_pairs = {(size, color) for size in sizes for color in colors}
        existing = {(v.size, v.color): v for v in clothes.variants.all()}

        for pair, variant in existing.items():
            if pair not in desired_pairs:
                variant.delete()

        for size, color in desired_pairs:
            if (size, color) not in existing:
                ClothesVariant.objects.create(
                    clothes=clothes,
                    size=size,
                    color=color,
                    stock=default_stock,
                )

    def create(self, validated_data):
        sizes = self._normalize_values(validated_data.pop('sizes', []))
        colors = self._normalize_values(validated_data.pop('colors', []))
        default_stock = validated_data.pop('default_stock', 0)
        clothes = Clothes.objects.create(**validated_data)

        if sizes and colors:
            self._sync_variants(clothes, sizes, colors, default_stock)

        return clothes

    def update(self, instance, validated_data):
        sizes = validated_data.pop('sizes', None)
        colors = validated_data.pop('colors', None)
        default_stock = validated_data.pop('default_stock', 0)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sizes is not None and colors is not None:
            normalized_sizes = self._normalize_values(sizes)
            normalized_colors = self._normalize_values(colors)
            if normalized_sizes and normalized_colors:
                self._sync_variants(instance, normalized_sizes, normalized_colors, default_stock)

        return instance


class ClothesVariantCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating variants"""
    class Meta:
        model = ClothesVariant
        fields = ['size', 'color', 'stock']
