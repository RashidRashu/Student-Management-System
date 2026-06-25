from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),   # kept for superuser DB access only; not linked in UI
    path('', include('students.urls')),
]
