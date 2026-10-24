"""Configuración de la aplicación Agentes."""

from django.apps import AppConfig


class AgentesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agentes"
    verbose_name = "Plataforma de Agentes Inteligentes"
