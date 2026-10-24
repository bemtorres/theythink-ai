"""Modelos ORM de Django vinculados a las tablas de la plataforma de agentes."""

from django.db import models


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=100, unique=True, verbose_name="Nombre de usuario")
    password_hash = models.CharField(max_length=255, verbose_name="Hash de contraseña")
    rol = models.CharField(max_length=50, default="admin", verbose_name="Rol")
    creado_en = models.CharField(max_length=50, blank=True, verbose_name="Creado en")

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.usuario} ({self.rol})"


class Agente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre identificador")
    perfil = models.TextField(blank=True, default="", verbose_name="Perfil descriptivo")
    conocimiento = models.TextField(blank=True, default="", verbose_name="Conocimiento directo")
    memoria = models.TextField(blank=True, default="", verbose_name="Memoria activa")
    identidad_clave = models.CharField(max_length=100, blank=True, default="", verbose_name="Clave de identidad")
    identidad_custom = models.TextField(blank=True, default="", verbose_name="Prompt de identidad personalizado")
    avatar_url = models.CharField(max_length=500, blank=True, default="", verbose_name="URL de avatar")
    creado_en = models.CharField(max_length=50, blank=True, verbose_name="Creado en")

    class Meta:
        db_table = "agentes"
        verbose_name = "Agente"
        verbose_name_plural = "Agentes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class FuenteConocimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre de la fuente")
    contenido = models.TextField(blank=True, default="", verbose_name="Contenido")
    creado_en = models.CharField(max_length=50, blank=True, verbose_name="Creado en")

    class Meta:
        db_table = "fuentes_conocimiento"
        verbose_name = "Fuente de Conocimiento"
        verbose_name_plural = "Fuentes de Conocimiento"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class AgenteFuente(models.Model):
    pk = models.CompositePrimaryKey("agente", "fuente")
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, db_column="agente_id")
    fuente = models.ForeignKey(FuenteConocimiento, on_delete=models.CASCADE, db_column="fuente_id")

    class Meta:
        db_table = "agente_fuentes"
        verbose_name = "Asociación Agente-Fuente"
        verbose_name_plural = "Asociaciones Agente-Fuente"

    def __str__(self):
        return f"{self.agente.nombre} <-> {self.fuente.nombre}"


class SesionChat(models.Model):
    id = models.AutoField(primary_key=True)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, db_column="agente_id", verbose_name="Agente")
    titulo = models.CharField(max_length=255, default="Nueva conversación", verbose_name="Título del hilo")
    creado_en = models.CharField(max_length=50, blank=True, verbose_name="Creado en")
    actualizado_en = models.CharField(max_length=50, blank=True, verbose_name="Actualizado en")

    class Meta:
        db_table = "sesiones_chat"
        verbose_name = "Sesión de Chat"
        verbose_name_plural = "Sesiones de Chat"
        ordering = ["-actualizado_en"]

    def __str__(self):
        return f"{self.agente.nombre} - {self.titulo} (#{self.id})"


class Conversacion(models.Model):
    id = models.AutoField(primary_key=True)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, db_column="agente_id", verbose_name="Agente")
    sesion = models.ForeignKey(
        SesionChat,
        on_delete=models.CASCADE,
        db_column="sesion_id",
        null=True,
        blank=True,
        verbose_name="Sesión",
    )
    fecha = models.CharField(max_length=20, verbose_name="Fecha")
    hora = models.CharField(max_length=20, verbose_name="Hora")
    rol = models.CharField(max_length=20, verbose_name="Rol (user/assistant)")
    mensaje = models.TextField(verbose_name="Mensaje")

    class Meta:
        db_table = "conversaciones"
        verbose_name = "Mensaje de Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ["id"]

    def __str__(self):
        return f"[{self.rol}] {self.agente.nombre} ({self.fecha} {self.hora})"


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=100, unique=True, verbose_name="Clave técnica")
    nombre = models.CharField(max_length=150, verbose_name="Nombre visible")
    descripcion = models.TextField(blank=True, default="", verbose_name="Descripción")
    prompt = models.TextField(blank=True, default="", verbose_name="System Prompt")
    es_sistema = models.IntegerField(default=0, verbose_name="Es rol de sistema")
    creado_en = models.CharField(max_length=50, blank=True, verbose_name="Creado en")
    actualizado_en = models.CharField(max_length=50, blank=True, verbose_name="Actualizado en")

    class Meta:
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.clave})"


class Grupo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del grupo")

    class Meta:
        db_table = "grupos"
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class AgenteGrupo(models.Model):
    pk = models.CompositePrimaryKey("agente", "grupo")
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, db_column="agente_id")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, db_column="grupo_id")

    class Meta:
        db_table = "agente_grupos"
        verbose_name = "Asignación Agente-Grupo"
        verbose_name_plural = "Asignaciones Agente-Grupo"

    def __str__(self):
        return f"{self.agente.nombre} in {self.grupo.nombre}"
