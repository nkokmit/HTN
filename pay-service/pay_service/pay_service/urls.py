from django.contrib import admin
from django.urls import path
from app.views import HealthView, PaymentCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('payments/', PaymentCreate.as_view()),
]
