from django.test import TestCase
from unittest.mock import patch, MagicMock
from M6_Comunidad_y_Colaboración.services.ai_service import AIService
from M6_Comunidad_y_Colaboración.services.math_solver import MathSolver

class AIServiceTest(TestCase):
    def setUp(self):
        self.ai_service = AIService()
    
    @patch('openai.ChatCompletion.create')
    def test_generar_respuesta_exitosa(self, mock_openai):
        # Mock de respuesta de OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "La respuesta es x = 4"
        mock_response.usage.total_tokens = 50
        mock_openai.return_value = mock_response
        
        resultado = self.ai_service.generar_respuesta("Resuelve 2x + 2 = 10")
        
        self.assertTrue(resultado['exito'])
        self.assertEqual(resultado['respuesta'], "La respuesta es x = 4")
        self.assertEqual(resultado['tokens_utilizados'], 50)
    
    @patch('openai.ChatCompletion.create')
    def test_generar_respuesta_error(self, mock_openai):
        mock_openai.side_effect = Exception("API Error")
        
        resultado = self.ai_service.generar_respuesta("Test")
        
        self.assertFalse(resultado['exito'])
        self.assertIn('error', resultado)

class MathSolverTest(TestCase):
    def setUp(self):
        self.math_solver = MathSolver()
    
    def test_detectar_categoria_algebra(self):
        texto = "Resuelve la ecuación 2x + 5 = 13"
        resultado = self.math_solver.analizar_problema(texto)
        
        self.assertEqual(resultado['categoria'], 'algebra')
        self.assertEqual(resultado['nivel'], 'secundaria')
    
    def test_detectar_categoria_calculo(self):
        texto = "Calcula la derivada de x^2 + 3x"
        resultado = self.math_solver.analizar_problema(texto)
        
        self.assertEqual(resultado['categoria'], 'calculo')
        self.assertEqual(resultado['nivel'], 'universitario')
    
    def test_estimar_dificultad(self):
        texto_facil = "Suma 2 + 2"
        texto_dificil = "Resuelve el sistema de ecuaciones diferenciales"
        
        resultado_facil = self.math_solver.analizar_problema(texto_facil)
        resultado_dificil = self.math_solver.analizar_problema(texto_dificil)
        
        self.assertLess(resultado_facil['dificultad'], resultado_dificil['dificultad'])