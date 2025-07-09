from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from M1_Gestion_de_Usuarios.views import logout_


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Paginas_Inicio.urls')),
    path('', include('M1_Gestion_de_Usuarios.urls')),
    path('', include('M2_Contenido_Educativo.urls')),
    path('logout/', logout_, name='logout'),
    path('cursos/', include('M5_cursos_contenido.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
