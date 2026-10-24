"""Definición de plantillas y generadores de prompts para los agentes.

Este módulo construye de manera dinámica los System Prompts inyectando la
identidad del rol, el perfil de la persona, las bases de conocimiento y la
memoria continua, además del prompt para evaluar y consolidar nuevos recuerdos.
"""

MEMORY_PROMPT_TEMPLATE = """Analiza la conversación.

Determina si apareció información NUEVA y RELEVANTE
que debería recordarse para futuras conversaciones.

Solo devuelve información que sea:
- útil
- persistente
- relevante para el usuario
- diferente de lo que ya existe en la memoria

Si no existe información nueva, responde:

NO_MEMORIA

Si existe información nueva, devuelve únicamente
los recuerdos que deberían almacenarse.

MEMORIA ACTUAL:
{memory}

CONVERSACIÓN:
{conversation}"""

NAME_MARKER = "[____]"
DOCUMENT_MARKER = "[información del documento]"
NO_MEMORY_TOKEN = "NO_MEMORIA"

REGLA_CONCISION_TOKENS = """DIRECTRICES OBLIGATORIAS DE RESPUESTA Y CONTROL DE TOKENS:
- Responde de forma breve, clara y directa.
- Utiliza únicamente la información necesaria para responder.
- No repitas la pregunta.
- Evita introducciones, conclusiones y explicaciones innecesarias.
- Prioriza respuestas de 2 a 5 frases."""


def process_identity(identity_prompt: str, person_name: str) -> str:
    """Procesa los marcadores en el prompt del rol."""
    name = person_name.strip() or "el tema de conversación"
    processed = identity_prompt.replace(NAME_MARKER, name)
    processed = processed.replace(
        DOCUMENT_MARKER, "la información disponible en la base de conocimiento"
    )
    return processed


def build_system_prompt(role_prompt: str, profile: str, knowledge: str, memory: str) -> str:
    """Construye el System Prompt completo para DeepSeek."""
    knowledge_text = knowledge.strip() if knowledge.strip() else "(sin conocimientos previos)"
    memory_text = memory.strip() if memory.strip() else "(sin memorias almacenadas)"

    return f"""{role_prompt}

PERFIL:
{profile.strip()}

BASE DE CONOCIMIENTO:
{knowledge_text}

MEMORIA:
{memory_text}

{REGLA_CONCISION_TOKENS}"""


def build_memory_prompt(memory: str, conversation: str) -> str:
    """Construye el prompt de evaluación de memoria para identificar nuevos hechos."""
    memory_text = memory.strip() if memory.strip() else "(sin memorias almacenadas)"
    return MEMORY_PROMPT_TEMPLATE.format(
        memory=memory_text,
        conversation=conversation.strip(),
    )


# Alias en español
PLANTILLA_MEMORIA = MEMORY_PROMPT_TEMPLATE
MARCA_NOMBRE = NAME_MARKER
MARCA_DOCUMENTO = DOCUMENT_MARKER
procesar_identidad = process_identity
construir_system_prompt = build_system_prompt
construir_prompt_memoria = build_memory_prompt
