from django.contrib import admin
from django.urls import path
from app.views import HealthView, RecommendationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('recommendations/', RecommendationView.as_view()),
]
