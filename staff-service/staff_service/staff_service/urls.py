from django.contrib import admin
from django.urls import path
from app.views import HealthView, StaffBookManageView, StaffBookManageDetailView

urlpatterns = [
	path('admin/', admin.site.urls),
	path('health/', HealthView.as_view()),
	path('staff/books/', StaffBookManageView.as_view()),
	path('staff/books/<int:book_id>/', StaffBookManageDetailView.as_view()),
]

