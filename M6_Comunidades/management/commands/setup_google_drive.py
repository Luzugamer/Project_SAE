from django.core.management.base import BaseCommand
from M6_Comunidades.google_drive_service import GoogleDriveService
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Configurar autenticación inicial de Google Drive'
    
    def handle(self, *args, **options):
        self.stdout.write("Configurando Google Drive...")
        
        # Verificar que existen los directorios necesarios
        credentials_dir = os.path.dirname(settings.GOOGLE_DRIVE_CREDENTIALS_FILE)
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
            self.stdout.write(f"Directorio creado: {credentials_dir}")
        
        try:
            # Intentar autenticar
            drive_service = GoogleDriveService()
            self.stdout.write(
                self.style.SUCCESS("✅ Google Drive configurado correctamente!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error configurando Google Drive: {str(e)}")
            )