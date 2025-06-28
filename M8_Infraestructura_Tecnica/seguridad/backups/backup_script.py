# Script para respaldo automático (RQ122)
import os
from datetime import datetime
from django.conf import settings

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
    
    # Ejemplo para PostgreSQL (requiere pg_dump instalado)
    os.system(f'pg_dump -U {settings.DATABASES["default"]["USER"]} -h {settings.DATABASES["default"]["HOST"]} {settings.DATABASES["default"]["NAME"]} > {backup_file}')