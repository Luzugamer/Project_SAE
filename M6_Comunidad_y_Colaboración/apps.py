from django.apps import AppConfig


class M6ComunidadYColaboraciónConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'M6_Comunidad_y_Colaboración'
    verbose_name = 'Comunidades de Estudio'

    def ready(self):
        import M6_Comunidad_y_Colaboración.signals