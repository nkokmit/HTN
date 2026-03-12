from django.contrib import admin
from django.urls import path
from app.views import HealthView, ManagerNoteListCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view()),
    path('manager/notes/', ManagerNoteListCreate.as_view()),
]
