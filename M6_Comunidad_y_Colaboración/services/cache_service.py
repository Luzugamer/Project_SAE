from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class CacheService:
    """
    Servicio para manejo de cache de respuestas
    """
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'AI_CACHE_TIMEOUT', 3600)  # 1 hora
        self.cache_prefix = 'ai_response_'
    
    def generar_clave_cache(self, pregunta: str, contexto: str = '') -> str:
        """
        Genera una clave única para el cache
        """
        contenido = f"{pregunta}:{contexto}"
        return self.cache_prefix + hashlib.md5(
            contenido.encode('utf-8')
        ).hexdigest()
    
    def obtener_respuesta_cache(self, pregunta: str, contexto: str = '') -> dict:
        """
        Obtiene respuesta del cache si existe
        """
        clave = self.generar_clave_cache(pregunta, contexto)
        return cache.get(clave)
    
    def guardar_respuesta_cache(self, pregunta: str, respuesta: dict, contexto: str = ''):
        """
        Guarda respuesta en cache
        """
        clave = self.generar_clave_cache(pregunta, contexto)
        cache.set(clave, respuesta, self.cache_timeout)
    
    def limpiar_cache_usuario(self, session_id: str):
        """
        Limpia cache relacionado con un usuario
        """
        # Implementar según necesidades específicas
        pass