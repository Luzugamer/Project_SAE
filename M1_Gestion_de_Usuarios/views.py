from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from user_agents import parse
import hashlib
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import UsuarioRegistroForm, UsuarioLoginForm, OTPVerificationForm, Setup2FAForm, DispositivoConfiableForm, CambiarPasswordForm
from .models import Usuario, DispositivoUsuario, NotificacionSeguridad
from .utils import detectar_patron_login_sospechoso, get_client_ip, get_location_from_ip, enviar_notificacion_email
from cloudinary import CloudinaryImage

def registro_view(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = Usuario.objects.create_user(
                correo_electronico=form.cleaned_data['correo_electronico'],
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                password=form.cleaned_data['password']
            )
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'M1_Gestion_de_Usuarios/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo_electronico']
            password = form.cleaned_data['password']

            user = authenticate(request, correo_electronico=correo, password=password)

            if user is not None:
                try:
                    # Verificar dispositivo
                    dispositivo, es_nuevo = verificar_dispositivo(request, user)
                    
                    # Detectar patrones sospechosos
                    ip_actual = get_client_ip(request)
                    es_sospechoso, motivo = detectar_patron_login_sospechoso(user, ip_actual)
                    
                    if es_sospechoso:
                        # Crear notificación de actividad sospechosa
                        NotificacionSeguridad.objects.create(
                            usuario=user,
                            tipo='inicio_sesion_sospechoso',
                            titulo='Actividad sospechosa detectada',
                            mensaje=f'Se detectó actividad sospechosa: {motivo}',
                            ip_origen=ip_actual,
                            dispositivo=dispositivo
                        )
                        
                        # Enviar email de alerta
                        enviar_alerta_actividad_sospechosa(user, motivo, dispositivo)
                    
                    # Si tiene 2FA habilitado y el dispositivo no es confiable
                    if user.is_two_factor_enabled and not dispositivo.es_confiable:
                        # Almacenar datos en sesión para la verificación 2FA
                        request.session['pre_2fa_user_id'] = user.id
                        request.session['pre_2fa_device_id'] = dispositivo.id
                        return redirect('verify_2fa')
                    
                    # Login directo si no tiene 2FA o dispositivo es confiable
                    return complete_login(request, user, dispositivo)
                    
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error en verificación de dispositivo: {e}")
                    form.add_error(None, 'Error interno del servidor. Intenta nuevamente.')
            else:
                form.add_error(None, 'Correo electrónico o contraseña inválidos.')
    else:
        form = UsuarioLoginForm()

    return render(request, 'M1_Gestion_de_Usuarios/login.html', {'form': form})


def complete_login(request, user, dispositivo):
    """Completa el proceso de login con la nueva estructura de roles"""
    # Actualizar última sesión
    user.ultima_sesion = timezone.now()
    user.save()
    login(request, user)
    
    # Redireccionar según rol (ahora accedemos directamente al campo rol)
    if not user.rol:  # Si no tiene rol asignado
        messages.error(request, 'Usuario sin rol asignado. Contacte al administrador.')
        return redirect('login')
    
    # Redirecciones basadas en el rol
    if user.rol == 'administrador':
        return redirect('/admin/')
    elif user.rol == 'profesor':
        return redirect('pag_profe')
    else:
        return redirect('pag_estu')


@login_required
@require_http_methods(["POST"])
def editar_perfil_completo(request):
    """Vista para editar perfil completo (sin foto)"""
    try:
        user = request.user
        
        # Actualizar campos del usuario
        user.nombre = request.POST.get('nombre', user.nombre)
        user.apellido = request.POST.get('apellido', user.apellido)
        user.correo_electronico = request.POST.get('correo', user.correo_electronico)
        user.institucion = request.POST.get('institucion', user.institucion)
        user.genero = request.POST.get('genero', user.genero)
        user.direccion = request.POST.get('direccion', user.direccion)
        user.sobre_mi = request.POST.get('sobre_mi', user.sobre_mi)
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'nombre': user.nombre,
            'apellido': user.apellido,
            'correo': user.correo_electronico,
            'institucion': user.institucion or '',
            'genero': user.genero or '',
            'direccion': user.direccion or '',
            'sobre_mi': user.sobre_mi or ''
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar el perfil: {str(e)}'
        })


@login_required
def subir_foto_perfil(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        user = request.user
        foto = request.FILES['foto_perfil']
        user.foto_perfil = foto
        user.save()
        return JsonResponse({
            'success': True,
            'message': 'Foto actualizada con éxito',
            'foto_url': user.foto_perfil.url
        })
    return JsonResponse({'success': False, 'message': 'Archivo no válido'}, status=400)

@login_required
def perfil_usuario_view(request):
    return render(request, 'M1_Gestion_de_Usuarios/perfil_usuario.html', {
        'usuario': request.user
    })
    
def perfil_image(request):
    img = CloudinaryImage(
        request.user.foto_perfil.public_id
        if request.user.foto_perfil else ''
    ).build_url(
        width=200, height=200, crop="thumb",
        default_image="usuarios/fotos_perfil/default_image.png"
    )
    return render(request, 'perfil.html', {'perfil_url': img})

@never_cache
def logout_(request):
    if request.user.is_authenticated:
        request.user.cierre_sesion = timezone.now()
        request.user.save()
    logout(request)
    return redirect('descripcion')


@login_required
def eliminar_cuenta_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Tu cuenta ha sido eliminada exitosamente.')
        return redirect('descripcion')

    return redirect('perfil_usuario')


def enviar_notificacion_nuevo_dispositivo(usuario, dispositivo):
    """Envía notificación por email de nuevo dispositivo"""
    subject = 'Nuevo dispositivo detectado en tu cuenta'
    message = f"""
    Hola {usuario.nombre},
    
    Se ha detectado un inicio de sesión desde un nuevo dispositivo:
    
    Dispositivo: {dispositivo.nombre_dispositivo}
    Ubicación: {dispositivo.ciudad}, {dispositivo.pais}
    Fecha y hora: {dispositivo.primer_acceso.strftime('%d/%m/%Y %H:%M:%S')}
    
    Si fuiste tú, puedes ignorar este mensaje.
    Si no reconoces este inicio de sesión, te recomendamos cambiar tu contraseña inmediatamente.
    
    Saludos,
    Equipo de Seguridad
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.correo_electronico],
        fail_silently=True,
    )
    
def enviar_alerta_actividad_sospechosa(usuario, motivo, dispositivo):
    """Envía alerta por email de actividad sospechosa"""
    subject = '⚠️ Actividad sospechosa en tu cuenta'
    message = f"""
    Hola {usuario.nombre},
    
    Se ha detectado actividad sospechosa en tu cuenta:
    
    Motivo: {motivo}
    Dispositivo: {dispositivo.nombre_dispositivo}
    Ubicación: {dispositivo.ciudad}, {dispositivo.pais}
    Fecha y hora: {dispositivo.ultimo_acceso.strftime('%d/%m/%Y %H:%M:%S')}
    IP: {dispositivo.ip_address}
    
    Si fuiste tú, puedes ignorar este mensaje.
    Si no reconoces esta actividad, te recomendamos:
    1. Cambiar tu contraseña inmediatamente
    2. Revisar tus dispositivos confiables
    3. Habilitar la autenticación de dos factores
    
    Saludos,
    Equipo de Seguridad
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.correo_electronico],
        fail_silently=True,
    )

@login_required
def marcar_principal_view(request, dispositivo_id):
    usuario = request.user
    dispositivo = get_object_or_404(DispositivoUsuario, id=dispositivo_id, usuario=usuario)

    if request.method == 'POST':
        # Desmarcar cualquier dispositivo anterior como principal
        usuario.dispositivos.update(es_principal=False)
        dispositivo.es_principal = True
        dispositivo.es_confiable = True
        dispositivo.save()
        messages.success(request, 'Dispositivo marcado como principal.')
        return redirect('dispositivos')

    return redirect('dispositivos')


@login_required
def dispositivos_view(request):
    dispositivos = request.user.dispositivos.filter(activo=True).order_by('-ultimo_acceso')
    hay_principal = dispositivos.filter(es_principal=True).exists()

    return render(request, 'M1_Gestion_de_Usuarios/dispositivos.html', {
        'dispositivos': dispositivos,
        'hay_principal': hay_principal
    })


@login_required
def marcar_confiable_view(request, dispositivo_id):
    dispositivo = get_object_or_404(
        DispositivoUsuario,
        id=dispositivo_id,
        usuario=request.user
    )

    if request.method == 'POST':
        dispositivo.es_confiable = True
        dispositivo.save()

        messages.success(request, f'Dispositivo {dispositivo.nombre_dispositivo} marcado como confiable.')
        return redirect('dispositivos')

    return redirect('dispositivos')


@login_required
def revocar_dispositivo_view(request, dispositivo_id):
    """Vista para revocar un dispositivo confiable"""
    dispositivo = get_object_or_404(
        DispositivoUsuario, 
        id=dispositivo_id, 
        usuario=request.user
    )
    
    if request.method == 'POST':
        dispositivo.activo = False
        dispositivo.es_confiable = False
        dispositivo.save()
        messages.success(request, f'Dispositivo {dispositivo.nombre_dispositivo} revocado correctamente.')
        return redirect('dispositivos')
    
    return render(request, 'M1_Gestion_de_Usuarios/revocar_dispositivo.html', {
        'dispositivo': dispositivo
    })


@login_required
def cerrar_sesion_dispositivo_view(request, dispositivo_id):
    dispositivo = get_object_or_404(DispositivoUsuario, id=dispositivo_id, usuario=request.user)

    if dispositivo.es_principal:
        messages.error(request, "No puedes cerrar sesión del dispositivo principal.")
        return redirect('dispositivos')

    if request.method == 'POST':
        dispositivo.activo = False
        dispositivo.save()
        messages.success(request, "Sesión cerrada correctamente para el dispositivo.")
        return redirect('dispositivos')
    
    return redirect('dispositivos')


def verify_2fa_view(request):
    """Vista para verificar código 2FA"""
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['pre_2fa_user_id']
    device_id = request.session['pre_2fa_device_id']
    user = get_object_or_404(Usuario, id=user_id)
    dispositivo = get_object_or_404(DispositivoUsuario, id=device_id)
    
    if request.method == 'POST':
        otp_form = OTPVerificationForm(request.POST)
        trust_form = DispositivoConfiableForm(request.POST)
        
        if otp_form.is_valid():
            otp_code = otp_form.cleaned_data['otp_code']
            
            if user.verify_otp(otp_code):
                # Código correcto
                if trust_form.is_valid() and trust_form.cleaned_data.get('marcar_confiable'):
                    dispositivo.es_confiable = True
                    dispositivo.save()
                
                # Limpiar sesión temporal
                del request.session['pre_2fa_user_id']
                del request.session['pre_2fa_device_id']
                
                return complete_login(request, user, dispositivo)
            else:
                otp_form.add_error('otp_code', 'Código de verificación incorrecto.')
    else:
        otp_form = OTPVerificationForm()
        trust_form = DispositivoConfiableForm()
    
    return render(request, 'M1_Gestion_de_Usuarios/verify_2fa.html', {
        'otp_form': otp_form,
        'trust_form': trust_form,
        'user': user
    })


@login_required
def setup_2fa_view(request):
    """Vista para configurar 2FA"""
    user = request.user
    
    if request.method == 'POST':
        form = Setup2FAForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            
            if user.verify_otp(otp_code):
                user.is_two_factor_enabled = True
                user.save()
                
                # Crear notificación
                NotificacionSeguridad.objects.create(
                    usuario=user,
                    tipo='2fa_habilitado',
                    titulo='Autenticación de dos factores habilitada',
                    mensaje='Has habilitado exitosamente la autenticación de dos factores en tu cuenta.'
                )
                
                messages.success(request, 'Autenticación de dos factores habilitada correctamente.')
                return redirect('perfil_usuario')  # Redireccionar a página de perfil
            else:
                form.add_error('otp_code', 'Código de verificación incorrecto.')
    else:
        form = Setup2FAForm()
        # Generar secret si no existe
        user.generate_otp_secret()
    
    qr_code = user.get_qr_code()
    
    return render(request, 'M1_Gestion_de_Usuarios/setup_2fa.html', {
        'form': form,
        'qr_code': qr_code,
        'secret_key': user.otp_secret_key
    })


@login_required
def disable_2fa_view(request):
    """Vista para deshabilitar 2FA"""
    if request.method == 'POST':
        user = request.user
        user.is_two_factor_enabled = False
        user.otp_secret_key = None
        user.save()
        
        # Crear notificación
        NotificacionSeguridad.objects.create(
            usuario=user,
            tipo='2fa_deshabilitado',
            titulo='Autenticación de dos factores deshabilitada',
            mensaje='Has deshabilitado la autenticación de dos factores en tu cuenta.'
        )
        
        messages.success(request, 'Autenticación de dos factores deshabilitada.')
        return redirect('perfil_usuario')
    
    return render(request, 'M1_Gestion_de_Usuarios/disable_2fa.html')


@login_required
def cambiar_password_view(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['password_actual']):
                user.set_password(form.cleaned_data['nueva_password'])
                user.save()
                update_session_auth_hash(request, user)  # Para no cerrar sesión
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('perfil_usuario')
            else:
                form.add_error('password_actual', 'Contraseña actual incorrecta.')
    else:
        form = CambiarPasswordForm()

    return render(request, 'M1_Gestion_de_Usuarios/cambiar_password.html', {'form': form})


def get_device_fingerprint(request):
    """Genera un fingerprint único del dispositivo"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    ip_address = get_client_ip(request)
    
    # Crear fingerprint basado en varios factores
    fingerprint_data = f"{user_agent}{accept_language}{accept_encoding}{ip_address}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]  # Usar solo 16 caracteres


def parse_user_agent(user_agent_string):
    """Parsea el user agent para extraer información del dispositivo"""
    user_agent = parse(user_agent_string)
    
    # Manejar casos donde los valores pueden ser None
    browser_family = user_agent.browser.family or "Desconocido"
    browser_version = user_agent.browser.version_string or ""
    os_family = user_agent.os.family or "Desconocido"
    os_version = user_agent.os.version_string or ""
    
    return {
        'navegador': f"{browser_family} {browser_version}".strip(),
        'sistema_operativo': f"{os_family} {os_version}".strip(),
        'es_mobile': user_agent.is_mobile,
        'es_tablet': user_agent.is_tablet,
        'es_pc': user_agent.is_pc
    }


def verificar_dispositivo(request, usuario):
    """Verifica si el dispositivo es conocido y confiable"""
    fingerprint = get_device_fingerprint(request)
    ip_address = get_client_ip(request)
    
    try:
        dispositivo = DispositivoUsuario.objects.get(
            usuario=usuario, 
            fingerprint=fingerprint
        )
        # Actualizar último acceso
        dispositivo.ultimo_acceso = timezone.now()
        dispositivo.ip_address = ip_address
        dispositivo.save()
        return dispositivo, False  # Dispositivo conocido
    except DispositivoUsuario.DoesNotExist:
        # Dispositivo nuevo
        user_agent_info = parse_user_agent(request.META.get('HTTP_USER_AGENT', ''))
        location_info = get_location_from_ip(ip_address)
        
        # Crear nombre del dispositivo más descriptivo
        if user_agent_info['es_mobile']:
            tipo_dispositivo = "Móvil"
        elif user_agent_info['es_tablet']:
            tipo_dispositivo = "Tablet"
        else:
            tipo_dispositivo = "PC"
        
        nombre_dispositivo = f"{tipo_dispositivo} - {user_agent_info['navegador']}"
        
        try:
            dispositivo = DispositivoUsuario.objects.create(
                usuario=usuario,
                fingerprint=fingerprint,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=ip_address,
                navegador=user_agent_info['navegador'],
                sistema_operativo=user_agent_info['sistema_operativo'],
                ciudad=location_info.get('ciudad', ''),
                pais=location_info.get('pais', ''),
                nombre_dispositivo=nombre_dispositivo
            )
            
            # Crear notificación de nuevo dispositivo
            NotificacionSeguridad.objects.create(
                usuario=usuario,
                tipo='nuevo_dispositivo',
                titulo='Nuevo dispositivo detectado',
                mensaje=f'Se ha detectado un inicio de sesión desde un nuevo dispositivo: {dispositivo.nombre_dispositivo}',
                ip_origen=ip_address,
                dispositivo=dispositivo
            )
            
            # Enviar email de notificación
            enviar_notificacion_nuevo_dispositivo(usuario, dispositivo)
            
            return dispositivo, True  # Dispositivo nuevo
            
        except Exception as e:
            # Log del error para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creando dispositivo: {e}")
            raise e
        
@login_required
def send_verification_email(request):
    usuario = request.user

    asunto = "Verifica tu correo electrónico"
    mensaje = (
        f"Hola {usuario.nombre},\n\n"
        f"Gracias por registrarte en nuestra plataforma.\n"
        f"Por favor haz clic en el siguiente enlace para verificar tu correo electrónico:\n"
        f"https://tusitio.com/verificar-email/{usuario.pk}/\n\n"
        f"Si no solicitaste esto, ignora este mensaje.\n\n"
        f"Equipo de soporte"
    )

    enviado = enviar_notificacion_email(usuario, asunto, mensaje)

    if enviado:
        return JsonResponse({"success": True, "message": "Correo de verificación enviado."})
    else:
        return JsonResponse({"success": False, "message": "No se pudo enviar el correo."}, status=500)
    
    
@csrf_exempt
@login_required
def verify_code_ajax(request):
    """Verifica el código OTP enviado desde el modal"""
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_code = data.get('otp_code')
        
        user = request.user
        if user.verify_otp(otp_code):
            return JsonResponse({'success': True, 'message': 'Código correcto'})
        else:
            return JsonResponse({'success': False, 'message': 'Código incorrecto'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)