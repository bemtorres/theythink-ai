"""Orquestador cognitivo de agentes que interactúa con DeepSeek LLM y Django ORM."""

import os
from dotenv import load_dotenv
import openai

from agentes.lib.prompt import (
    construir_prompt_memoria,
    construir_system_prompt,
    procesar_identidad,
)
from .agent_service import (
    actualizar_memoria as actualizar_memoria_agente,
    agregar_memorias,
    obtener_agente,
)
from .base import HISTORIAL_RECIENTE, MODELO, SIN_MEMORIA
from .chat_service import guardar_mensaje, obtener_historial
from .knowledge_service import obtener_fuentes_agente
from .role_service import obtener_rol_por_clave


class AgenteDB:
    """Agente que gestiona sus datos, memoria y conversaciones en Django ORM con llamadas a DeepSeek."""

    def __init__(self, nombre):
        load_dotenv()
        self.nombre = nombre
        self.perfil = ""
        self.conocimiento = ""
        self.identidad = ""
        self.identidad_custom = ""
        self.memoria = ""
        self.client = self._crear_cliente()
        self.cargar_perfil()
        self.cargar_conocimiento()
        self.cargar_identidad()
        self.cargar_memoria()

    def _crear_cliente(self):
        """Crea el cliente de DeepSeek usando la API Key del entorno."""
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key or api_key == "tu_api_key":
            raise ValueError(
                "No se encontró una API Key válida de DeepSeek. "
                "Configura tu DEEPSEEK_API_KEY en el archivo .env."
            )
        return openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    def _enviar(self, mensajes, max_tokens=400):
        """Realiza una llamada a la API de DeepSeek."""
        try:
            respuesta = self.client.chat.completions.create(
                model=MODELO,
                messages=mensajes,
                max_tokens=max_tokens if max_tokens else 400,
            )
        except openai.AuthenticationError as error:
            raise RuntimeError(
                "La API Key de DeepSeek es inválida. Verifica tu .env."
            ) from error
        except openai.APIConnectionError as error:
            raise RuntimeError(
                "No se pudo conectar con DeepSeek. Revisa tu conexión a internet."
            ) from error
        except openai.RateLimitError as error:
            raise RuntimeError(
                "Límite de solicitudes alcanzado. Espera unos segundos e intenta de nuevo."
            ) from error
        except openai.APIError as error:
            raise RuntimeError(f"Error de la API de DeepSeek: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al contactar a DeepSeek: {error}") from error

        contenido = respuesta.choices[0].message.content
        return contenido.strip() if contenido else ""

    def obtener_nombre(self):
        """Extrae el nombre legible de la persona desde el perfil del agente."""
        lineas = self.perfil.splitlines()
        for indice, linea in enumerate(lineas):
            if linea.strip().startswith("NOMBRE:"):
                for siguiente in lineas[indice + 1:]:
                    if siguiente.strip():
                        return siguiente.strip()
        return self.nombre

    def construir_prompt(self):
        """Construye el System Prompt completo procesando rol, perfil, conocimientos y memoria."""
        _, _, prompt_rol = self.info_identidad()
        rol = procesar_identidad(prompt_rol, self.obtener_nombre())
        return construir_system_prompt(rol, self.perfil, self.conocimiento, self.memoria)

    def cargar_perfil(self):
        datos = obtener_agente(self.nombre)
        self.perfil = datos["perfil"] if datos else ""

    def cargar_conocimiento(self):
        """Construye el conocimiento desde las bases de conocimiento asociadas."""
        datos = obtener_agente(self.nombre)
        fuentes = obtener_fuentes_agente(self.nombre)
        partes = []
        for fuente in fuentes:
            texto = (fuente.get("contenido") or "").strip()
            if texto:
                nombre_fuente = fuente.get("nombre", "").strip()
                if nombre_fuente:
                    partes.append(f"[{nombre_fuente}]\n{texto}")
                else:
                    partes.append(texto)
        manual = (datos["conocimiento"] if datos else "").strip()
        if manual:
            partes.append(manual)
        self.conocimiento = "\n\n".join(partes)

    def cargar_identidad(self):
        datos = obtener_agente(self.nombre)
        self.identidad = datos["identidad_clave"] if datos else ""
        self.identidad_custom = datos["identidad_custom"] if datos else ""

    def info_identidad(self):
        """Devuelve (nombre, descripcion, prompt) consultando los roles de la base de datos."""
        if self.identidad_custom:
            return ("Identidad personalizada", "Prompt propio guardado en la base de datos.", self.identidad_custom)
        if self.identidad:
            rol = obtener_rol_por_clave(self.identidad)
            if rol:
                return (rol["nombre"], rol["descripcion"], rol["prompt"])
        rol_defecto = obtener_rol_por_clave("basic")
        if rol_defecto:
            return (rol_defecto["nombre"], rol_defecto["descripcion"], rol_defecto["prompt"])
        return ("Básico", "Agente experto en la base de conocimiento.", "Eres un asistente útil.")

    def cargar_memoria(self):
        datos = obtener_agente(self.nombre)
        self.memoria = datos["memoria"] if datos else ""

    def guardar_conversacion(self, rol, mensaje, sesion_id=None):
        guardar_mensaje(self.nombre, rol, mensaje, sesion_id=sesion_id)

    def obtener_historial(self, cantidad=HISTORIAL_RECIENTE, sesion_id=None):
        return obtener_historial(self.nombre, cantidad, sesion_id=sesion_id)

    def preguntar(self, mensaje, sesion_id=None, max_tokens=400):
        self.guardar_conversacion("user", mensaje, sesion_id=sesion_id)
        historial = self.obtener_historial(sesion_id=sesion_id)

        mensajes = [{"role": "system", "content": self.construir_prompt()}]
        for rol, contenido in historial:
            if contenido:
                mensajes.append({"role": rol, "content": contenido})

        respuesta = self._enviar(mensajes, max_tokens=max_tokens)
        if not respuesta:
            raise RuntimeError("DeepSeek devolvió una respuesta vacía.")

        self.guardar_conversacion("assistant", respuesta, sesion_id=sesion_id)
        return respuesta

    def actualizar_memoria(self, mensaje_usuario, respuesta):
        conversacion = f"Usuario: {mensaje_usuario}\nAgente: {respuesta}"
        prompt = construir_prompt_memoria(self.memoria, conversacion)
        try:
            contenido = self._enviar([{"role": "user", "content": prompt}], max_tokens=150)
        except RuntimeError:
            return []
        if not contenido or SIN_MEMORIA in contenido.upper():
            return []
        agregadas = agregar_memorias(self.nombre, contenido)
        if agregadas:
            self.cargar_memoria()
        return agregadas

    # Alias en inglés dentro de la clase
    ask = preguntar
    update_memory = actualizar_memoria
    build_prompt = construir_prompt
    load_profile = cargar_perfil
    load_knowledge = cargar_conocimiento
    load_identity = cargar_identidad
    load_memory = cargar_memoria
    save_conversation = guardar_conversacion
    get_history = obtener_historial


AgentDB = AgenteDB
