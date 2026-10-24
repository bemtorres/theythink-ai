"""Configuración del panel de administración de Django para los agentes."""

from django.contrib import admin
from .models import (
    Agente,
    Conversacion,
    FuenteConocimiento,
    Grupo,
    Rol,
    SesionChat,
    Usuario,
)


@admin.register(Agente)
class AgenteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "identidad_clave", "avatar_url", "creado_en")
    search_fields = ("nombre", "perfil", "identidad_clave")
    list_filter = ("identidad_clave",)
    readonly_fields = ("creado_en",)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("id", "clave", "nombre", "es_sistema", "actualizado_en")
    search_fields = ("clave", "nombre", "descripcion", "prompt")
    list_filter = ("es_sistema",)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(FuenteConocimiento)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "creado_en")
    search_fields = ("nombre", "contenido")


@admin.register(SesionChat)
class SesionChatAdmin(admin.ModelAdmin):
    list_display = ("id", "agente", "titulo", "actualizado_en", "creado_en")
    search_fields = ("titulo", "agente__nombre")
    list_filter = ("agente",)


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ("id", "agente", "sesion", "rol", "fecha", "hora")
    search_fields = ("mensaje", "agente__nombre")
    list_filter = ("rol", "agente")


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "rol", "creado_en")
    search_fields = ("usuario", "rol")
    list_filter = ("rol",)
