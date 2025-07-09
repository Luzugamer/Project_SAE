from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from M6_Comunidad_y_Colaboración.models import Conversacion, Mensaje
import json
from unittest.mock import patch  

class AsistenteViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_inicio_view(self):
        response = self.client.get(reverse('asistente:inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asistente Matemático')
    
    def test_asistente_ia_view(self):
        response = self.client.get(reverse('asistente:asistente_ia'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chat-container')
    
    def test_procesar_pregunta_view(self):
        # Crear conversación
        conversacion = Conversacion.objects.create(
            session_id='test-session',
            usuario=self.user
        )
        
        # Datos de la pregunta
        data = {
            'pregunta': 'Resuelve x + 2 = 5',
            'session_id': 'test-session'
        }
        
        with patch('M6_Comunidad_y_Colaboración.services.ai_service.AIService.generar_respuesta') as mock_ai:
            mock_ai.return_value = {
                'respuesta': 'x = 3',
                'tokens_utilizados': 25,
                'tiempo_respuesta': 1.5,
                'exito': True
            }
            
            response = self.client.post(
                reverse('asistente:procesar_pregunta'),
                data=json.dumps(data),
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['respuesta'], 'x = 3')
        
        # Verificar que se crearon los mensajes
        self.assertEqual(conversacion.mensajes.count(), 2)