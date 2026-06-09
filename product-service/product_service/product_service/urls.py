from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.views import HealthView, ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('', include(router.urls)),
]
