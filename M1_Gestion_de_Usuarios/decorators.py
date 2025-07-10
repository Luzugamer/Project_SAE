from django.http import HttpResponseForbidden
from functools import wraps

def rol_requerido(*roles_permitidos):
    """Decorador que verifica si el usuario tiene alguno de los roles permitidos"""
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Debes iniciar sesión.")
            
            if request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorador