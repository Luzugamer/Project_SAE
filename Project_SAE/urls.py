from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from M1_Gestion_de_Usuarios.views import logout_


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Paginas_Inicio.urls')),
    path('', include('M1_Gestion_de_Usuarios.urls')),
    path('logout/', logout_, name='logout'),
    path('seguridad/', include('M8_Infraestructura_Tecnica.seguridad.politicas.urls')), 
    path('dashboard/', include('M8_Infraestructura_Tecnica.dashboards.urls')),
    path('accesibilidad/', include('M8_Infraestructura_Tecnica.accesibilidad.urls')),
    path('ajustes-ui/', include('M8_Infraestructura_Tecnica.accesibilidad.ajustes_ui.urls')),
    path('modo-nocturno/', include('M8_Infraestructura_Tecnica.accesibilidad.modo_nocturno.urls')),
    path('formularios/', include('M8_Infraestructura_Tecnica.formularios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
