from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import Comunidad, Mensaje
from .google_drive_service import GoogleDriveService
import json
from datetime import datetime
from django.contrib.auth.models import User
from .models import Perfil

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        Perfil.objects.create(usuario=instance)
@receiver(post_save, sender=Comunidad)
def crear_carpeta_google_drive(sender, instance, created, **kwargs):
    """Crear carpeta en Google Drive cuando se crea una nueva comunidad"""
    if created and not instance.google_drive_folder_id:
        try:
            drive_service = GoogleDriveService()
            folder_name = f"Comunidad_{instance.nombre}_{instance.id}"
            
            folder_id = drive_service.create_folder(folder_name)
            
            if folder_id:
                instance.google_drive_folder_id = folder_id
                instance.save(update_fields=['google_drive_folder_id'])
                
                # Crear archivo inicial de información de la comunidad
                info_content = f"""INFORMACIÓN DE LA COMUNIDAD
=================================
Nombre: {instance.nombre}
Descripción: {instance.descripcion}
Creador: {instance.creador.get_full_name() or instance.creador.username}
Fecha de creación: {instance.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')}
Es pública: {'Sí' if instance.es_publica else 'No'}

=================================
HISTORIAL DE MENSAJES
=================================
"""
                
                drive_service.upload_file(
                    info_content,
                    f"info_comunidad_{instance.id}.txt",
                    folder_id
                )
                
        except Exception as e:
            print(f"Error creando carpeta para comunidad {instance.id}: {str(e)}")

@receiver(pre_delete, sender=Comunidad)
def eliminar_carpeta_google_drive(sender, instance, **kwargs):
    """Eliminar carpeta de Google Drive cuando se elimina una comunidad"""
    if instance.google_drive_folder_id:
        try:
            drive_service = GoogleDriveService()
            drive_service.delete_folder(instance.google_drive_folder_id)
        except Exception as e:
            print(f"Error eliminando carpeta de Google Drive para comunidad {instance.id}: {str(e)}")

@receiver(post_save, sender=Mensaje)
def guardar_mensaje_google_drive(sender, instance, created, **kwargs):
    """Guardar mensaje en Google Drive cuando se crea o actualiza"""
    if instance.comunidad.google_drive_folder_id:
        try:
            drive_service = GoogleDriveService()
            
            # Formato del mensaje
            mensaje_formato = f"""
[{instance.timestamp.strftime('%d/%m/%Y %H:%M:%S')}] {instance.autor.get_full_name() or instance.autor.username}
Tipo: {instance.get_tipo_display()}
Mensaje: {instance.contenido}
{'='*50}
"""
            
            # Buscar archivo de mensajes existente
            filename = f"mensajes_comunidad_{instance.comunidad.id}.txt"
            archivos = drive_service.search_files_in_folder(
                instance.comunidad.google_drive_folder_id, 
                filename
            )
            
            if archivos:
                # Actualizar archivo existente
                # Nota: Para simplificar, aquí crearemos un nuevo archivo
                # En producción, podrías implementar la lectura y actualización del contenido
                file_id = archivos[0]['id']
                
                # Leer contenido actual (implementación simplificada)
                nuevo_contenido = mensaje_formato
                drive_service.update_file(file_id, nuevo_contenido)
                
            else:
                # Crear nuevo archivo de mensajes
                file_id = drive_service.upload_file(
                    mensaje_formato,
                    filename,
                    instance.comunidad.google_drive_folder_id
                )
                
                if file_id and not instance.google_drive_file_id:
                    instance.google_drive_file_id = file_id
                    instance.save(update_fields=['google_drive_file_id'])
                    
        except Exception as e:
            print(f"Error guardando mensaje en Google Drive: {str(e)}")