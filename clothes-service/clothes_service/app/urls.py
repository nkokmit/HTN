from django.urls import path
from .views import (
    ClothesListView,
    ClothesDetailView,
    ClothesVariantListView,
    ClothesVariantDetailView,
)

urlpatterns = [
    # Clothes endpoints
    path('clothes/', ClothesListView.as_view(), name='clothes-list'),
    path('clothes/<int:pk>/', ClothesDetailView.as_view(), name='clothes-detail'),
    
    # Variants endpoints
    path('clothes/<int:clothes_id>/variants/', ClothesVariantListView.as_view(), name='variant-list'),
    path('clothes/<int:clothes_id>/variants/<int:variant_id>/', ClothesVariantDetailView.as_view(), name='variant-detail'),
]
