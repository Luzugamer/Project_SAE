# -*- coding: utf-8 -*-
from openai import OpenAI
from django.conf import settings
from typing import Dict, Any
import time
from .math_solver import MathSolver
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_tokens = 1000
        self.temperature = 0.1
        self.math_solver = MathSolver()

    def generar_respuesta(self, pregunta: str, contexto: list = None) -> Dict[str, Any]:
        try:
            start_time = time.time()

            # Detectar si es una integral simple
            if "integrar" in pregunta.lower() or "∫" in pregunta or "integral de" in pregunta.lower():
                solucion = self.math_solver.resolver_integral(pregunta)
                if "error" in solucion:
                    respuesta = f"Error: {solucion['error']}"
                else:
                    respuesta = f"""
🚀 **Resolución simbólica usando SymPy**:
- Paso a paso simbólico: `{solucion['pasos']}`
- Resultado final: `{solucion['resultado']}`
- LaTeX: `$${solucion['latex']}$$`
"""
                end_time = time.time()
                return {
                    'respuesta': respuesta,
                    'tokens_utilizados': 0,
                    'tiempo_respuesta': round(end_time - start_time, 2),
                    'exito': True
                }

            # Si no es una integral, usar GPT-4
            mensajes = self._construir_contexto(pregunta, contexto)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cambia a "gpt-4" si tienes acceso
                messages=mensajes,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            end_time = time.time()

            return {
                'respuesta': response.choices[0].message.content,
                'tokens_utilizados': response.usage.total_tokens,
                'tiempo_respuesta': round(end_time - start_time, 2),
                'exito': True
            }

        except Exception as e:
            logger.error("Error en AIService: %s", str(e))
            return {
                'respuesta': 'Ocurrió un error al procesar tu pregunta.',
                'tokens_utilizados': 0,
                'tiempo_respuesta': 0,
                'exito': False,
                'error': str(e)
            }

    def _construir_contexto(self, pregunta: str, contexto: list = None) -> list:
        prompt_sistema = (
            "Eres un asistente de matemáticas para secundaria y universidad. "
            "Responde paso a paso y usa LaTeX si es necesario."
        )

        mensajes = [{"role": "system", "content": prompt_sistema}]

        if contexto:
            for msg in contexto[-5:]:
                role = "user" if msg['tipo'] == 'usuario' else "assistant"
                mensajes.append({"role": role, "content": msg['contenido']})

        mensajes.append({"role": "user", "content": pregunta})

        return mensajes
