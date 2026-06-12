"""
URL configuration for customer_service project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import (
    CustomerListCreate,
    HealthView,
    LoginView,
    ManagerNoteListCreate,
    RegisterView,
    StaffBookManageDetailView,
    StaffBookManageView,
    UsersListCreate,
    UserDetailUpdateView,
    UserAddressViewSet, # 1. Import ViewSet địa chỉ vào đây
)

# 2. Khởi tạo Router để tự động sinh các đường dẫn CRUD cho addresses/
router = DefaultRouter()
router.register(r'addresses', UserAddressViewSet, basename='user-address')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('users/', UsersListCreate.as_view()),
    path('users/<int:user_id>/', UserDetailUpdateView.as_view()),
    path('customers/', CustomerListCreate.as_view()),
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('staff/products/', StaffBookManageView.as_view()),
    path('staff/products/<int:product_id>/', StaffBookManageDetailView.as_view()),
    path('manager/notes/', ManagerNoteListCreate.as_view()),
    
    # 3. Nhúng toàn bộ các tuyến đường của router địa chỉ vào urlpatterns
    path('', include(router.urls)), 
]