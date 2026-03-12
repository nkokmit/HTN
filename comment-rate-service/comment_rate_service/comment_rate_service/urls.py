from django.contrib import admin
from django.urls import path
from app.views import HealthView, RatingListCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('ratings/', RatingListCreate.as_view()),
]
