from django.contrib import admin
from django.urls import path
from app.views import HealthView, OrderListCreate, OrderDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('orders/', OrderListCreate.as_view()),
    path('orders/<int:order_id>/', OrderDetail.as_view()),
]
