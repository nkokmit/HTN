from django.contrib import admin
from django.urls import path
from app.views import HealthView, CatalogView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('catalog/books/', CatalogView.as_view()),
]
