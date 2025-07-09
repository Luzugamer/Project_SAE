from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'comunidad'

urlpatterns = [
    path('inicio/', views.home, name='inicio'),
    path('principio/', views.principio, name='principio'),

    path('mis-comunidades/', views.mis_comunidades, name='mis_comunidades'),
    path('crear/', views.crear_comunidad, name='crear_comunidad'),
    path('comunidad-gestion/', views.comunidad_gestion, name='comunidad_gestion'),
    path('comunidad-gestion/<int:comunidad_id>/', views.comunidad_gestion, name='comunidad_gestion'),

    path('comunidad/<int:comunidad_id>/', views.comunidad_detalle, name='comunidad_detalle'),
    path('comunidad/invitacion/<str:codigo_invitacion>/', views.unirse_por_invitacion, name='unirse_por_invitacion'),
    path('<int:comunidad_id>/invitar/', views.invitar_estudiantes, name='invitar_estudiantes'),
    path('comunidad/<int:comunidad_id>/editar/', views.editar_comunidad, name='editar_comunidad'),
    
    path('<int:comunidad_id>/eliminar/', views.eliminar_comunidad, name='eliminar_comunidad'),
    path('<int:comunidad_id>/zona_descanso/', views.zona_descanso, name='zona_descanso'),

    path('<int:comunidad_id>/salir/', views.salir_comunidad, name='salir_comunidad'),
    path('invitacion/<str:codigo_invitacion>/', views.unirse_por_invitacion, name='unirse_por_invitacion'),
    path('<int:comunidad_id>/invitar/', views.invitar_estudiantes, name='invitar_estudiantes'),
    path('<int:comunidad_id>/gestionar-miembros/', views.gestionar_miembros, name='gestionar_miembros'),
    path('<int:comunidad_id>/compartir/', views.compartir_comunidad, name='compartir_comunidad'),
    
    path('verificar-nombre/', views.verificar_nombre_comunidad, name='verificar_nombre_comunidad'),
    
    path('<int:comunidad_id>/regenerar-codigo/', views.regenerar_codigo, name='regenerar_codigo'),
    path('<int:comunidad_id>/enviar-invitaciones/', views.enviar_invitaciones_email, name='enviar_invitaciones_email'),

    path('<int:comunidad_id>/zona_descanso/', views.zona_descanso, name='zona_descanso'),
    path('<int:comunidad_id>/reportar/', views.reportar_comunidad, name='reportar_comunidad'),
    
    path('buscar/', views.buscar_comunidades, name='buscar_comunidades'),
    path('comunidad/', views.comunidad, name='comunidad'),
    
    path('<int:comunidad_id>/unirse-conversacion/', views.unirse_a_conversacion, name='unirse_conversacion'),
    path('<int:comunidad_id>/enviar-mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('<int:comunidad_id>/obtener-mensajes/', views.obtener_mensajes, name='obtener_mensajes'),
    path('<int:comunidad_id>/enviar-mensaje-privado/', views.enviar_mensaje_privado, name='enviar_mensaje_privado'),
    path('<int:comunidad_id>/mensajes-privados/<int:usuario_id>/', views.obtener_mensajes_privados, name='obtener_mensajes_privados'),
    path('<int:comunidad_id>/miembros-en-linea/', views.obtener_miembros_en_linea, name='obtener_miembros_en_linea'),
    path('<int:comunidad_id>/actualizar-conexion/', views.actualizar_estado_conexion, name='actualizar_conexion'),
    path('<int:comunidad_id>/historial-mensajes/', views.recuperar_mensajes_historial, name='historial_mensajes'),
    
    path('asistente_ia/', views.AsistenteIAView.as_view(), name='asistente_ia'),
    path('api/procesar-pregunta/', views.ProcesarPreguntaView.as_view(), name='procesar_pregunta'),
    path('api/historial/', views.HistorialView.as_view(), name='historial'),
    path('api/limpiar-conversacion/', views.LimpiarConversacionView.as_view(), name='limpiar_conversacion'),
    
    
    
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)