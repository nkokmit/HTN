from rest_framework import serializers
from django.db import transaction
from .models import Book, Category, Electronics, Fashion, Health, Home, Product, Toy


class CategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = Category
		fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):

	class Meta:
		model = Book
		exclude = ["product"]


class ElectronicsSerializer(serializers.ModelSerializer):

	class Meta:
		model = Electronics
		exclude = ["product"]


class FashionSerializer(serializers.ModelSerializer):

	class Meta:
		model = Fashion
		exclude = ["product"]


class HomeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Home
		exclude = ["product"]


class ToySerializer(serializers.ModelSerializer):
	class Meta:
		model = Toy
		exclude = ["product"]


class HealthSerializer(serializers.ModelSerializer):
	class Meta:
		model = Health
		exclude = ["product"]


class ProductSerializer(serializers.ModelSerializer):
	category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
	category_name = serializers.CharField(required=False, write_only=True)
	category_detail = CategorySerializer(source="category", read_only=True)

	product_type = serializers.CharField(required=False, write_only=True)
	book = BookSerializer(required=False)
	electronics = ElectronicsSerializer(required=False)
	fashion = FashionSerializer(required=False)
	home = HomeSerializer(required=False)
	toy = ToySerializer(required=False)
	health = HealthSerializer(required=False)

	class Meta:
		model = Product
		fields = [
			"id",
			"name",
			"price",
			"stock",
			"category",
			"category_name",
			"category_detail",
			"product_type",
			"book",
			"electronics",
			"fashion",
			"home",
			"toy",
			"health",
		]
		read_only_fields = ["id", "category_detail"]

	PRODUCT_TYPES = {"BOOK", "ELECTRONICS", "FASHION", "HOME", "TOY", "HEALTH"}
	CATEGORY_TYPE_MAP = {
		"BOOKS": "BOOK",
		"ELECTRONICS": "ELECTRONICS",
		"FASHION": "FASHION",
		"HOME": "HOME",
		"TOYS": "TOY",
		"HEALTH": "HEALTH",
	}

	def _detect_existing_type(self, product: Product) -> str | None:
		if hasattr(product, "book"):
			return "BOOK"
		if hasattr(product, "electronics"):
			return "ELECTRONICS"
		if hasattr(product, "fashion"):
			return "FASHION"
		if hasattr(product, "home"):
			return "HOME"
		if hasattr(product, "toy"):
			return "TOY"
		if hasattr(product, "health"):
			return "HEALTH"
		return None

	def _resolve_product_type(self, attrs: dict) -> str:
		explicit_type = attrs.get("product_type")
		category: Category = attrs.get("category")

		if explicit_type:
			normalized = explicit_type.upper()
			if normalized not in self.PRODUCT_TYPES:
				raise serializers.ValidationError(
					{"product_type": "product_type must be BOOK, ELECTRONICS, FASHION, HOME, TOY, or HEALTH."}
				)
			return normalized

		inferred = self.CATEGORY_TYPE_MAP.get(category.name.strip().upper(), "") if category else ""
		if inferred in self.PRODUCT_TYPES:
			return inferred

		raise serializers.ValidationError(
			{
				"product_type": (
					"Cannot infer subtype from category name. "
					"Provide product_type or use category name BOOKS/ELECTRONICS/FASHION/HOME/TOYS/HEALTH."
				)
			}
		)

	def validate(self, attrs):
		category = attrs.get("category")
		category_name = attrs.get("category_name")
		if not category and not category_name:
			raise serializers.ValidationError(
				{"category": "Provide category id or category_name."}
			)

		if not category and category_name:
			category, _ = Category.objects.get_or_create(name=category_name.strip())
			attrs["category"] = category

		product_type = self._resolve_product_type(attrs)

		subtype_payload = {
			"BOOK": attrs.get("book"),
			"ELECTRONICS": attrs.get("electronics"),
			"FASHION": attrs.get("fashion"),
			"HOME": attrs.get("home"),
			"TOY": attrs.get("toy"),
			"HEALTH": attrs.get("health"),
		}[product_type]

		if not subtype_payload:
			raise serializers.ValidationError(
				{product_type.lower(): f"{product_type.lower()} data is required for {product_type}."}
			)

		attrs["_resolved_product_type"] = product_type
		return attrs

	@transaction.atomic
	def create(self, validated_data):
		product_type = validated_data.pop("_resolved_product_type")
		validated_data.pop("product_type", None)
		validated_data.pop("category_name", None)

		book_data = validated_data.pop("book", None)
		electronics_data = validated_data.pop("electronics", None)
		fashion_data = validated_data.pop("fashion", None)
		home_data = validated_data.pop("home", None)
		toy_data = validated_data.pop("toy", None)
		health_data = validated_data.pop("health", None)

		product = Product.objects.create(**validated_data)

		if product_type == "BOOK":
			Book.objects.create(product=product, **book_data)
		elif product_type == "ELECTRONICS":
			Electronics.objects.create(product=product, **electronics_data)
		elif product_type == "FASHION":
			Fashion.objects.create(product=product, **fashion_data)
		elif product_type == "HOME":
			Home.objects.create(product=product, **home_data)
		elif product_type == "TOY":
			Toy.objects.create(product=product, **toy_data)
		else:
			Health.objects.create(product=product, **health_data)

		return product

	def to_representation(self, instance):
		data = super().to_representation(instance)
		product_type = self._detect_existing_type(instance)
		data["product_type"] = product_type

		if product_type != "BOOK":
			data["book"] = None
		if product_type != "ELECTRONICS":
			data["electronics"] = None
		if product_type != "FASHION":
			data["fashion"] = None
		if product_type != "HOME":
			data["home"] = None
		if product_type != "TOY":
			data["toy"] = None
		if product_type != "HEALTH":
			data["health"] = None

		# Add some synthetic fields for frontend display without changing models
		# - description: short generated description
		# - icon: emoji hint per category
		# - price_display: localized price string
		# - sold: simple sold count derived from stock
		cat_name = getattr(instance.category, "name", "") if instance.category else ""
		emoji_map = {
			"Books": "📚",
			"Electronics": "🔌",
			"Fashion": "👗",
			"Home": "🏠",
			"Toys": "🎲",
			"Health": "💊",
		}
		data.setdefault("description", f"{instance.name} - Mô tả ngắn.")
		data.setdefault("icon", emoji_map.get(cat_name, "📦"))
		data.setdefault("price_display", f"{int(instance.price)}đ")
		# Derive a sold count from stock for demo purposes
		try:
			data.setdefault("sold", max(0, int(instance.stock) // 2))
		except Exception:
			data.setdefault("sold", "—")

		return data


