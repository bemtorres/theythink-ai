"""Actualiza la instantánea de agentes del prototipo sin modificar la base."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theythink.settings")
import django
django.setup()
from agentes import services as bd

bd.BASE_DATOS = str(ROOT / "agentes.db")
DESCRIPTIONS = {
    "bodega_jefe": "Convierte los problemas de inventario en propuestas concretas para una bodega más ordenada.",
    "bodega_trabajador": "Conoce cada rincón de la bodega. Te contará qué falla entre un conteo y el siguiente.",
    "tienda_jefe": "Una mirada comercial para conectar la experiencia del cliente con los próximos módulos.",
    "tienda_trabajador": "Entre pedidos, reposición y clientes difíciles, sabe qué necesita cambiar en la tienda.",
    "tarjetas_jefe": "Habla de pagos claros, trazabilidad y prioridades para desarrollar BeatPay Virtual.",
    "tarjetas_trabajador": "Reclamos, bloqueos y devoluciones: conoce el lado cotidiano de los medios de pago.",
    "transporte_jefe": "Piensa en rutas, entregas y en cómo conectar el courier con el resto de MusicPro.",
    "transporte_trabajador": "Diez años al volante y pocas ganas de llamadas innecesarias. Tiene mejoras que proponer.",
    "el_principito": "Una mirada curiosa para volver a encontrar lo esencial en las cosas pequeñas.",
    "sherlock_holmes": "Observa los detalles que pasan inadvertidos. Pon a prueba tu capacidad de deducción.",
    "don_quijote": "Ideales, aventuras y una conversación con un caballero que se niega a dejar de soñar.",
    "socrates": "Una buena pregunta puede cambiar tu respuesta. Examina tus ideas con el filósofo de Atenas.",
    "nikola_tesla": "Invención, electricidad y las preguntas de una mente que imaginó otro futuro.",
    "el_flaite_chileno": "Humor, música urbana y una conversación directa con un personaje de Santiago.",
    "hincha_colocolo": "Historias del Monumental, memoria alba y pasión por el fútbol chileno.",
    "hincha_udechile": "La mística azul, recuerdos de tribuna y una pasión que acompaña en las buenas y en las malas.",
}
DISPLAY_NAMES = {"don_quijote": "Don Quijote", "socrates": "Sócrates", "nikola_tesla": "Nikola Tesla", "el_principito": "El Principito", "el_flaite_chileno": "El Jordan", "hincha_colocolo": "El Albo Adicto", "hincha_udechile": "El Bullanguero"}
ROLES = {"bodega": "Bodega", "tienda": "Sucursal y tienda", "tarjetas": "BeatPay Virtual", "transporte": "Courier y transporte"}

def section(profile, label):
    match = re.search(r"(?:^|\n)" + re.escape(label) + r":\s*\n(.+?)(?=\n\s*\n|\Z)", profile, re.S)
    return match.group(1).strip() if match else ""

groups = bd.listar_grupos()
agents = []
for key in bd.listar_agentes():
    data = bd.obtener_agente(key)
    profile = data["perfil"]
    name = DISPLAY_NAMES.get(key, section(profile, "NOMBRE").splitlines()[0])
    group = next((g["nombre"] for g in groups if key in g["agentes"]), "")
    category = "clientes" if key.startswith("cliente_") else "equipo" if group == "MusicPro" else "personajes"
    if category == "clientes":
        area = key.split("_")[1]
        role = "Cliente · " + ROLES[area]
        description = section(profile, "EXPERIENCIA SIMULADA")
        starters = ["¿Cómo fue tu experiencia con MusicPro?", "¿Qué te gustaría mejorar del servicio?", "¿Qué te haría volver a comprar?"]
    elif category == "equipo":
        area, job = key.split("_")
        role = ("Jefatura" if job == "jefe" else "Operaciones") + " · " + ROLES[area]
        description = DESCRIPTIONS[key]
        starters = ["¿Qué desarrollarías primero en tu módulo?", "¿Qué problema resolvería esa mejora?", "¿Cómo comprobarías que funciona?"] if job == "jefe" else ["¿Qué es lo más difícil de tu turno?", "¿Qué falla en el sistema actual?", "¿Cómo te gustaría hacer esa tarea?"]
    else:
        role = {"nikola_tesla": "Inventor e ingeniero", "socrates": "Filosofía y preguntas", "sherlock_holmes": "Detective consultor", "don_quijote": "Caballero andante", "el_principito": "Explorador de estrellas", "el_flaite_chileno": "Música y cultura urbana", "hincha_colocolo": "Fútbol · Colo-Colo", "hincha_udechile": "Fútbol · Universidad de Chile"}.get(key, "Personaje")
        description = DESCRIPTIONS.get(key, section(profile, "PERSONALIDAD"))
        starters = ["¿Qué es lo que más te interesa del mundo?", "¿Qué pregunta debería hacerme hoy?", "Cuéntame algo desde tu perspectiva."]
    agents.append(dict(id=key, name=name, group=group, category=category, role=role, description=description, avatar=data["avatar_url"], starters=starters))

# Alternar personajes y perfiles de MusicPro para dar variedad al primer vistazo.
preferred = ["el_principito", "tienda_jefe", "sherlock_holmes", "cliente_bodega_feliz", "socrates", "bodega_trabajador", "nikola_tesla", "cliente_tienda_problemas"]
agents.sort(key=lambda a: (preferred.index(a["id"]) if a["id"] in preferred else len(preferred), a["name"]))
target = ROOT / "static" / "preview" / "agentes.js"
target.write_text("window.previewAgents = " + json.dumps(agents, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
print(f"Instantánea exportada: {len(agents)} agentes")
