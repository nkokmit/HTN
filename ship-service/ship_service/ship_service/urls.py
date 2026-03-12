from django.contrib import admin
from django.urls import path
from app.views import HealthView, ShipmentCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('shipments/', ShipmentCreate.as_view()),
]
