"""Configuración principal de URLs para THEYTHINK AI en Django."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("agentes.urls")),
]
