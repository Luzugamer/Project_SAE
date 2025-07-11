from django.urls import path
from . import views

urlpatterns = [
    
    # Rutas login y last login
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_, name='logout'),
    path('eliminar-cuenta/', views.eliminar_cuenta_view, name='eliminar_cuenta'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('dispositivos/cerrar_sesion/<int:dispositivo_id>/', views.cerrar_sesion_dispositivo_view, name='cerrar_sesion_dispositivo'),
    path('perfil/', views.perfil_usuario_view, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil_completo, name='editar_perfil_completo'),
    path('perfil/send-verification-email/', views.send_verification_email, name='send_verification_email'),
    path('verificar-codigo/', views.verify_code_ajax, name='verify_code'),
    path('perfil/subir-foto-perfil/', views.subir_foto_perfil, name='subir_foto_perfil'),

    # Rutas para 2FA
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
    path('setup-2fa/', views.setup_2fa_view, name='setup_2fa'),
    path('disable-2fa/', views.disable_2fa_view, name='disable_2fa'),
    
    # Gestión de dispositivos
    path('dispositivos/', views.dispositivos_view, name='dispositivos'),
    path('dispositivos/confiar/<int:dispositivo_id>/', views.marcar_confiable_view, name='marcar_confiable'),
    path('dispositivos/principal/<int:dispositivo_id>/', views.marcar_principal_view, name='marcar_principal'),
    path('dispositivos/cerrar_sesion/<int:dispositivo_id>/', views.cerrar_sesion_dispositivo_view, name='cerrar_sesion_dispositivo'),
    path('dispositivos/revocar/<int:dispositivo_id>/', views.revocar_dispositivo_view, name='revocar_dispositivo'),
    
]
