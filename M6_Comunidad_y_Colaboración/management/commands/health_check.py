from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from M6_Comunidad_y_Colaboración.services.ai_service import AIService
import requests

class Command(BaseCommand):
    help = 'Health check del sistema'
    
    def handle(self, *args, **options):
        checks = {
            'database': self.check_database(),
            'cache': self.check_cache(),
            'ai_service': self.check_ai_service(),
        }
        
        all_healthy = all(checks.values())
        
        if all_healthy:
            self.stdout.write(self.style.SUCCESS('✓ Sistema saludable'))
        else:
            self.stdout.write(self.style.ERROR('✗ Sistema con problemas'))
        
        for check, status in checks.items():
            symbol = '✓' if status else '✗'
            self.stdout.write(f'{symbol} {check}')
        
        return 0 if all_healthy else 1
    
    def check_database(self):
        try:
            connection.ensure_connection()
            return True
        except Exception:
            return False
    
    def check_cache(self):
        try:
            cache.set('health_check', 'ok', 10)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False
    
    def check_ai_service(self):
        try:
            ai_service = AIService()
            # Test básico sin usar tokens reales
            return True
        except Exception:
            return False