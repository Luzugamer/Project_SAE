from django.apps import AppConfig

class M1GestionDeUsuariosConfig(AppConfig):
    name = 'M1_Gestion_de_Usuarios'

    def ready(self):
        import M1_Gestion_de_Usuarios.signals