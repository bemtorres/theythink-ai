"""Servicio de autenticación y gestión de usuarios."""

from werkzeug.security import check_password_hash, generate_password_hash
from agentes.models import Usuario
from .base import _ahora_str


def crear_usuario(usuario, password, rol="admin"):
    """Crea un nuevo usuario con contraseña hasheada."""
    usuario = usuario.strip().lower()
    if not usuario or not password:
        raise ValueError("El nombre de usuario y la contraseña no pueden estar vacíos.")
    if Usuario.objects.filter(usuario=usuario).exists():
        raise ValueError(f"El usuario '{usuario}' ya existe.")
    p_hash = generate_password_hash(password)
    user = Usuario.objects.create(
        usuario=usuario,
        password_hash=p_hash,
        rol=rol,
        creado_en=_ahora_str(),
    )
    return user.id


def verificar_usuario(usuario, password):
    """Verifica las credenciales y devuelve el usuario si son válidas."""
    user = Usuario.objects.filter(usuario=usuario.strip().lower()).first()
    if user and check_password_hash(user.password_hash, password):
        return {"id": user.id, "usuario": user.usuario, "rol": user.rol}
    return None


def obtener_usuario(usuario_id):
    """Devuelve un usuario por su ID sin password hash."""
    user = Usuario.objects.filter(id=usuario_id).first()
    if user:
        return {
            "id": user.id,
            "usuario": user.usuario,
            "rol": user.rol,
            "creado_en": user.creado_en,
        }
    return None


def obtener_usuario_por_nombre(usuario):
    """Devuelve un usuario por su nombre de usuario."""
    user = Usuario.objects.filter(usuario=usuario.strip().lower()).first()
    if user:
        return {
            "id": user.id,
            "usuario": user.usuario,
            "rol": user.rol,
            "creado_en": user.creado_en,
        }
    return None


def listar_usuarios():
    """Devuelve la lista de usuarios registrados."""
    return [
        {
            "id": u.id,
            "usuario": u.usuario,
            "rol": u.rol,
            "creado_en": u.creado_en,
        }
        for u in Usuario.objects.order_by("-id")
    ]


def actualizar_usuario(usuario_id, nuevo_usuario=None, nuevo_password=None, nuevo_rol=None):
    """Actualiza los datos de un usuario."""
    user = Usuario.objects.filter(id=usuario_id).first()
    if not user:
        raise ValueError("El usuario no existe.")
    if nuevo_usuario:
        nuevo_usuario = nuevo_usuario.strip().lower()
        if Usuario.objects.filter(usuario=nuevo_usuario).exclude(id=usuario_id).exists():
            raise ValueError(f"Ya existe un usuario con el nombre '{nuevo_usuario}'.")
        user.usuario = nuevo_usuario
    if nuevo_rol:
        user.rol = nuevo_rol
    if nuevo_password and nuevo_password.strip():
        user.password_hash = generate_password_hash(nuevo_password.strip())
    user.save()


def eliminar_usuario(usuario_id):
    """Elimina un usuario por su ID."""
    deleted, _ = Usuario.objects.filter(id=usuario_id).delete()
    return deleted > 0


def inicializar_admin_por_defecto():
    """Crea el usuario admin inicial si no existe ninguno."""
    if not Usuario.objects.exists():
        crear_usuario("admin", "admin123", "admin")
