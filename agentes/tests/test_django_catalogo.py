"""Suite de pruebas exhaustiva para THEYTHINK AI en Django."""

import json
import os
import re
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "theythink.settings")
import django
django.setup()

from django.test import Client
from agentes import services as bd
from agentes.seeders import crear_perfiles


class DjangoPlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        crear_perfiles()
        cls.client = Client()

    def get_catalog_data(self, response):
        text = response.content.decode("utf-8")
        match = re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>', text, re.S)
        self.assertIsNotNone(match, "No se encontró el bloque catalog-data en el HTML.")
        return json.loads(match.group(1))

    def test_01_home_catalogo_publico(self):
        """Verifica que el catálogo público cargue correctamente sin requerir login."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Explorar · THEYTHINK AI", res.content.decode("utf-8"))
        agents = self.get_catalog_data(res)
        self.assertGreater(len(agents), 20)
        sherlock = next((a for a in agents if a["id"] == "sherlock_holmes"), None)
        self.assertIsNotNone(sherlock)
        self.assertEqual(sherlock["name"], "Sherlock Holmes")

    def test_02_grupos_filtro(self):
        """Verifica el filtrado por grupo existente e inexistente."""
        grupos = bd.listar_grupos()
        if grupos:
            gid = grupos[0]["id"]
            res = self.client.get(f"/?grupo={gid}")
            self.assertEqual(res.status_code, 200)

        # Grupo inexistente debe responder 404
        res_404 = self.client.get("/?grupo=999999")
        self.assertEqual(res_404.status_code, 404)

    def test_03_proteccion_rutas_privadas(self):
        """Verifica que chat y dashboard exijan inicio de sesión previo."""
        unauth_client = Client()
        res_chat = unauth_client.get("/agente/sherlock_holmes")
        self.assertEqual(res_chat.status_code, 302)
        self.assertIn("/login", res_chat.headers.get("Location", ""))

        res_dash = unauth_client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 302)
        self.assertIn("/login", res_dash.headers.get("Location", ""))

    def test_04_autenticacion_y_acceso(self):
        """Verifica el flujo de login, sesión y acceso a vistas protegidas."""
        client = Client()
        # Login fallido
        res_bad = client.post("/login", {"usuario": "no_existe", "password": "wrong"})
        self.assertEqual(res_bad.status_code, 401)

        if not bd.obtener_usuario_por_nombre("testuser"):
            bd.crear_usuario("testuser", "secreto123", rol="admin")
        res_ok = client.post("/login", {"usuario": "testuser", "password": "secreto123"})
        self.assertEqual(res_ok.status_code, 302)

        # Acceso a chat y dashboard
        res_chat = client.get("/agente/sherlock_holmes")
        self.assertEqual(res_chat.status_code, 200)
        self.assertIn("Sherlock Holmes", res_chat.content.decode("utf-8"))

        res_dash = client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)

        res_wa = client.get("/agente/sherlock_holmes/whatsapp")
        self.assertEqual(res_wa.status_code, 200)

        res_tg = client.get("/agente/sherlock_holmes/telegram")
        self.assertEqual(res_tg.status_code, 200)

        # Logout
        res_logout = client.get("/logout")
        self.assertEqual(res_logout.status_code, 302)

    def test_05_api_endpoints(self):
        """Verifica los endpoints de la API JSON de fuentes y agentes."""
        client = Client()
        res_fuentes = client.get("/api/fuentes")
        self.assertEqual(res_fuentes.status_code, 200)
        data = json.loads(res_fuentes.content.decode("utf-8"))
        self.assertIn("fuentes", data)

        res_agente = client.get("/api/agente/sherlock_holmes")
        self.assertEqual(res_agente.status_code, 200)
        agente_data = json.loads(res_agente.content.decode("utf-8"))
        self.assertEqual(agente_data["nombre"], "sherlock_holmes")


if __name__ == "__main__":
    unittest.main()
