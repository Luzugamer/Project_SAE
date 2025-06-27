from .google_drive_service import GoogleDriveService
from .models import Comunidad, Mensaje

class ComunidadGoogleDriveManager:
    def __init__(self):
        self.drive_service = GoogleDriveService()
    
    def sincronizar_comunidad(self, comunidad_id):
        """Sincronizar todos los mensajes de una comunidad con Google Drive"""
        try:
            comunidad = Comunidad.objects.get(id=comunidad_id)
            
            if not comunidad.google_drive_folder_id:
                # Crear carpeta si no existe
                folder_name = f"Comunidad_{comunidad.nombre}_{comunidad.id}"
                folder_id = self.drive_service.create_folder(folder_name)
                comunidad.google_drive_folder_id = folder_id
                comunidad.save()
            
            # Obtener todos los mensajes
            mensajes = Mensaje.objects.filter(comunidad=comunidad).order_by('timestamp')
            
            # Crear contenido completo
            contenido_completo = f"""HISTORIAL COMPLETO DE MENSAJES
Comunidad: {comunidad.nombre}
Sincronizado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Total de mensajes: {mensajes.count()}

{'='*50}

"""
            
            for mensaje in mensajes:
                contenido_completo += f"""[{mensaje.timestamp.strftime('%d/%m/%Y %H:%M:%S')}] {mensaje.autor.get_full_name() or mensaje.autor.username}
{mensaje.contenido}
{'-'*30}

"""
            
            # Subir archivo completo
            filename = f"historial_completo_comunidad_{comunidad.id}.txt"
            file_id = self.drive_service.upload_file(
                contenido_completo,
                filename,
                comunidad.google_drive_folder_id
            )
            
            return True, f"Sincronización exitosa. Archivo ID: {file_id}"
            
        except Exception as e:
            return False, f"Error en sincronización: {str(e)}"
    
    def generar_backup_todas_comunidades(self):
        """Generar backup de todas las comunidades"""
        comunidades = Comunidad.objects.all()
        resultados = []
        
        for comunidad in comunidades:
            exito, mensaje = self.sincronizar_comunidad(comunidad.id)
            resultados.append({
                'comunidad': comunidad.nombre,
                'exito': exito,
                'mensaje': mensaje
            })
        
        return resultados