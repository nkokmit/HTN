from django.contrib import admin
from django.urls import path
from app.views import HealthView, ShipmentCreate, ShipmentDetail, ShipmentStatusView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('shipments/', ShipmentCreate.as_view()),
    path('shipments/<int:shipment_id>/', ShipmentDetail.as_view()),
    path('shipments/order/<int:order_id>/', ShipmentStatusView.as_view()),
]
