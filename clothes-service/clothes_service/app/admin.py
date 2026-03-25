from django.contrib import admin
from .models import Clothes, ClothesVariant


@admin.register(Clothes)
class ClothesAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


@admin.register(ClothesVariant)
class ClothesVariantAdmin(admin.ModelAdmin):
    list_display = ['clothes', 'size', 'color', 'stock']
    search_fields = ['clothes__name', 'size', 'color']
    list_filter = ['clothes']
    ordering = ['clothes', 'size', 'color']
