from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
from decouple import config
import io
import logging

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Autenticar con Google Drive API usando variables de entorno"""
        try:
            creds = Credentials(
                token=None,  # token se obtiene al refrescar
                refresh_token=config("GOOGLE_REFRESH_TOKEN"),
                token_uri=config("GOOGLE_TOKEN_URI"),
                client_id=config("GOOGLE_CLIENT_ID"),
                client_secret=config("GOOGLE_CLIENT_SECRET"),
                scopes=["https://www.googleapis.com/auth/drive"]
            )

            if creds.expired or not creds.valid:
                creds.refresh(Request())

            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Error de autenticación con Google Drive: {str(e)}")
            self.service = None

    def create_folder(self, folder_name, parent_folder_id=None):
        """Crear una carpeta en Google Drive"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()
            logger.info(f"Carpeta '{folder_name}' creada con ID: {folder.get('id')}")
            return folder.get('id')
        except Exception as e:
            logger.error(f"Error creando carpeta '{folder_name}': {str(e)}")
            return None

    def delete_folder(self, folder_id):
        """Eliminar una carpeta de Google Drive"""
        try:
            self.service.files().delete(fileId=folder_id).execute()
            logger.info(f"Carpeta con ID '{folder_id}' eliminada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error eliminando carpeta con ID '{folder_id}': {str(e)}")
            return False

    def upload_file(self, file_content, filename, folder_id, mime_type='text/plain'):
        """Subir un archivo a una carpeta específica"""
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = MediaIoBaseUpload(
                io.BytesIO(file_content.encode('utf-8')),
                mimetype=mime_type
            )
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name'
            ).execute()
            logger.info(f"Archivo '{filename}' subido con ID: {file.get('id')}")
            return file.get('id')
        except Exception as e:
            logger.error(f"Error subiendo archivo '{filename}': {str(e)}")
            return None

    def update_file(self, file_id, new_content):
        """Actualizar el contenido de un archivo existente"""
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(new_content.encode('utf-8')),
                mimetype='text/plain'
            )
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            logger.info(f"Archivo con ID '{file_id}' actualizado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error actualizando archivo con ID '{file_id}': {str(e)}")
            return False

    def search_files_in_folder(self, folder_id, filename=None):
        """Buscar archivos en una carpeta específica"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if filename:
                query += f" and name='{filename}'"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, modifiedTime)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error(f"Error buscando archivos en carpeta '{folder_id}': {str(e)}")
            return []
