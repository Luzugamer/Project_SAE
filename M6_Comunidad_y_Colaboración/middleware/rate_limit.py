from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import time

class RateLimitMiddleware:
    """
    Middleware para limitar requests por IP
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = getattr(settings, 'MAX_REQUESTS_PER_HOUR', 100)
        self.window_size = 3600  # 1 hora
    
    def __call__(self, request):
        # Solo aplicar rate limiting a endpoints de IA
        if request.path.startswith('/api/'):
            if not self.is_allowed(request):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Try again later.'
                }, status=429)
        
        response = self.get_response(request)
        return response
    
    def is_allowed(self, request):
        """
        Verifica si la request está dentro del límite
        """
        ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{ip}'
        
        requests_data = cache.get(cache_key, [])
        current_time = time.time()
        
        # Filtrar requests dentro de la ventana de tiempo
        requests_data = [
            req_time for req_time in requests_data 
            if current_time - req_time < self.window_size
        ]
        
        if len(requests_data) >= self.max_requests:
            return False
        
        # Agregar request actual
        requests_data.append(current_time)
        cache.set(cache_key, requests_data, self.window_size)
        
        return True
    
    def get_client_ip(self, request):
        """
        Obtiene la IP del cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip