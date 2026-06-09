from django.contrib import admin
from django.urls import path
from app.views import HealthView, HomeSuggestionsView, ProductChatView, RecommendationView, TrackEventView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('recommendations/', RecommendationView.as_view()),
    path('home-suggestions/', HomeSuggestionsView.as_view()),
    path('chat/', ProductChatView.as_view()),
    path('events/', TrackEventView.as_view()),
]
