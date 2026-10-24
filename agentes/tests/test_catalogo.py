"""Regresiones de catálogo, presentación pública y acceso a conversaciones en Django."""
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.test import Client

from agentes import services as bd
import agentes.views as agentes_views
from agentes.seeders import crear_perfiles


class CatalogoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_db = bd.BASE_DATOS
        cls.original_django_db = settings.DATABASES['default']['NAME']
        cls.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        test_db = str(Path(cls.temp.name) / 'test.db')
        bd.BASE_DATOS = test_db
        settings.DATABASES['default']['NAME'] = test_db
        connections.close_all()

        call_command('migrate', verbosity=0)
        crear_perfiles()
        bd.crear_agente('perfil_nuevo', perfil='NOMBRE:\nPersona nueva\n\nPROFESIÓN:\nDocente', memoria='MEMORIA_PRIVADA_NO_PUBLICAR')
        bd.crear_agente('sin_perfil')
        cls.custom_group = bd.crear_grupo('Otro proyecto')
        bd.asignar_grupo('perfil_nuevo', cls.custom_group)

    @classmethod
    def tearDownClass(cls):
        bd.BASE_DATOS = cls.original_db
        settings.DATABASES['default']['NAME'] = cls.original_django_db
        connections.close_all()
        cls.temp.cleanup()

    def setUp(self):
        self.client = Client()

    def agents(self, response):
        text = response.content.decode("utf-8")
        match = re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>', text, re.S)
        return json.loads(match.group(1))

    def test_catalog_does_not_load_chat_details_or_expose_memory(self):
        with patch.object(agentes_views, 'load_agent_data', side_effect=AssertionError('Carga de detalle innecesaria')):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content_text = response.content.decode("utf-8")
        self.assertNotIn('MEMORIA_PRIVADA_NO_PUBLICAR', content_text)
        agents = self.agents(response)
        self.assertEqual(len(agents), 26)
        self.assertEqual(next(a for a in agents if a['id'] == 'perfil_nuevo')['name'], 'Persona nueva')
        self.assertEqual(next(a for a in agents if a['id'] == 'sin_perfil')['name'], 'Sin Perfil')
        self.assertEqual(sum(a['category'] == 'clientes' for a in agents), 8)

    def test_groups_are_live_and_unknown_group_is_not_found(self):
        response = self.client.get('/?grupo=' + str(self.custom_group))
        self.assertEqual(response.status_code, 200)
        new = next(a for a in self.agents(response) if a['id'] == 'perfil_nuevo')
        self.assertIn(self.custom_group, new['groups'])
        self.assertIn('Otro proyecto', response.content.decode("utf-8"))
        self.assertEqual(self.client.get('/?grupo=99999').status_code, 404)

    def test_chat_requires_login_and_preserves_presentation(self):
        response = self.client.get('/agente/bodega_jefe')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location', ''))
        
        session = self.client.session
        session['usuario'] = 'test'
        session.save()

        response = self.client.get('/agente/bodega_jefe')
        self.assertEqual(response.status_code, 200)
        content_text = response.content.decode("utf-8")
        self.assertIn('Roberto Salinas', content_text)
        self.assertIn('character-presentation', content_text)
        self.assertIn('id="form-mensaje"', content_text)
        self.assertIn('id="lista-sesiones-sidebar"', content_text)
        self.assertEqual(self.client.get('/login').status_code, 302)

    def test_existing_channels_and_dashboard_render(self):
        session = self.client.session
        session['usuario'] = 'test'
        session.save()
        for url in ['/dashboard', '/agente/bodega_jefe/whatsapp', '/agente/bodega_jefe/telegram']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_generated_avatars_survive_seeding(self):
        self.assertEqual(bd.obtener_agente('nikola_tesla')['avatar_url'], '/static/avatars/generated/nikola_tesla-v1.png')
        self.assertEqual(bd.obtener_agente('bodega_jefe')['avatar_url'], '/static/avatars/generated/bodega_jefe-v1.png')
        self.assertEqual(bd.avatar_local('../no-permitido'), '')


if __name__ == '__main__':
    unittest.main()
