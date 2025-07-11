import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


"""
    Almacenamiento personalizado para archivos y facilitar la migracion.
    Guarda los archivos en MEDIA_ROOT/temp_previews/
    y los sirve desde MEDIA_URL/temp_previews/
"""

class TempPreviewStorage(FileSystemStorage):

    def __init__(self, *args, **kwargs):
        location = os.path.join(settings.MEDIA_ROOT, 'temp_previews')
        base_url = settings.MEDIA_URL + 'temp_previews/'
        super().__init__(location=location, base_url=base_url, *args, **kwargs)


class LogosUniversidadesStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        location = os.path.join(settings.MEDIA_ROOT, 'logos_universidades')
        base_url = settings.MEDIA_URL + 'logos_universidades/'
        super().__init__(location=location, base_url=base_url, *args, **kwargs)

# Para archivos PDF de exámenes
class ExamenesUniversidadesStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        location = os.path.join(settings.MEDIA_ROOT, 'examenes_universidades')
        base_url = settings.MEDIA_URL + 'examenes_universidades/'
        super().__init__(location=location, base_url=base_url, *args, **kwargs)