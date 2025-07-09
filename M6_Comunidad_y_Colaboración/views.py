import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import uuid
import re
from urllib.parse import quote
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Comunidad, Mensaje, MiembroComunidad, Invitacion, Reporte, Perfil
from django.contrib.auth.models import User
import json

from .models import (
    Comunidad, MiembroComunidad, Mensaje, MensajePrivado, Invitacion, Perfil,
    SalaChat, MensajeSala, ConexionUsuario, HistorialMensajes, ROLES, ESTADO_MIEMBRO
)

def home(request):
    """Vista principal de bienvenida"""
    comunidades_destacadas = Comunidad.objects.filter(es_destacada=True, activa=True)[:6]
    todas_comunidades = Comunidad.objects.filter(activa=True).order_by('-fecha_creacion')
    
    context = {
        'comunidades_destacadas': comunidades_destacadas,
        'todas_comunidades': todas_comunidades,
    }
    return render(request, "foro/inicio.html", context)

@login_required 
def comunidad(request):
    return render(request, 'foro/comunidad.html')

@login_required
def comunidad_gestion(request):
    # Obtener todas las comunidades creadas por el profesor actual
    comunidades = Comunidad.objects.filter(creador=request.user, activa=True).order_by('-fecha_creacion')
    
    # Estadísticas generales
    total_comunidades = comunidades.count()
    comunidades_activas = comunidades.filter(activa=True).count()
    
    # Calcular total de miembros y mensajes
    total_miembros = 0
    total_mensajes = 0
    
    for comunidad in comunidades:
        total_miembros += comunidad.get_miembros_activos().count()
        total_mensajes += comunidad.mensajes.count()
    
    context = {
        'comunidades': comunidades,
        'total_comunidades': total_comunidades,
        'comunidades_activas': comunidades_activas,
        'total_miembros': total_miembros,
        'total_mensajes': total_mensajes,
    }
    
    return render(request, 'foro/comunidad_gestion.html', context)

@login_required
def crear_comunidad(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        institucion_afiliada = request.POST.get('institucion_afiliada', '').strip()
        icono = request.FILES.get('icono')
        # Validaciones
        if not nombre or not descripcion:
            messages.error(request, "Por favor completa todos los campos requeridos.")
            return render(request, "foro/crear_comunidad.html")
        
        if len(nombre) < 3:
            messages.error(request, "El nombre de la comunidad debe tener al menos 3 caracteres.")
            return render(request, "foro/crear_comunidad.html")
        
        if len(descripcion) < 10:
            messages.error(request, "La descripción debe tener al menos 10 caracteres.")
            return render(request, "foro/crear_comunidad.html")
        # Verificar si ya existe una comunidad con el mismo nombre
        if Comunidad.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, "Ya existe una comunidad con ese nombre.")
            return render(request, "foro/crear_comunidad.html")
        
        try:
            comunidad = Comunidad.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                institucion_afiliada=institucion_afiliada,
                creador=request.user,
                icono=icono if icono else None
            )
            # Agregar al creador como miembro profesor
            MiembroComunidad.objects.create(
                usuario=request.user,
                comunidad=comunidad,
                rol='profesor'
            )
            
            messages.success(request, f"Comunidad '{nombre}' creada exitosamente.")
            return redirect('comunidad:comunidad_gestion')
            
        except Exception as e:
            messages.error(request, f"Error al crear la comunidad: {str(e)}")
            return render(request, "foro/crear_comunidad.html")

    return render(request, "foro/crear_comunidad.html")

@login_required
def editar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Solo el creador puede editar
    if comunidad.creador != request.user:
        messages.error(request, "No tienes permisos para editar esta comunidad.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    if request.method == 'POST':
        comunidad.nombre = request.POST.get('nombre', comunidad.nombre)
        comunidad.descripcion = request.POST.get('descripcion', comunidad.descripcion)
        comunidad.institucion_afiliada = request.POST.get('institucion_afiliada', comunidad.institucion_afiliada)
        
        if request.FILES.get('icono'):
            comunidad.icono = request.FILES.get('icono')
        
        comunidad.save()
        messages.success(request, "Comunidad actualizada exitosamente.")
        return render(request, 'foro/comunidad_gestion.html', {'comunidad': comunidad})
    
    return render(request, "foro/editar_comunidad.html", {'comunidad': comunidad})

@login_required
def eliminar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Solo el creador puede eliminar la comunidad
    if comunidad.creador != request.user:
        messages.error(request, "No tienes permisos para eliminar esta comunidad.")
        return redirect('comunidad:comunidad_gestion')
    
    if request.method == 'POST':
        nombre_comunidad = comunidad.nombre
        comunidad.activa = False  # Desactivar en lugar de eliminar completamente
        comunidad.save()
        
        messages.success(request, f"Comunidad '{nombre_comunidad}' eliminada exitosamente.")
        return redirect('comunidad:comunidad_gestion')

    return redirect('comunidad:comunidad_gestion')

@login_required
def comunidad_detalle(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    
    if request.method == "POST":
        contenido = request.POST.get("contenido")

        if es_miembro:
            if contenido:
                Mensaje.objects.create(
                    comunidad=comunidad,
                    autor=request.user,
                    contenido=contenido
                )
                messages.success(request, "Mensaje enviado exitosamente.")
        else:
            # Usuario se une a la comunidad
            MiembroComunidad.objects.create(usuario=request.user, comunidad=comunidad)
            messages.success(request, f"Te has unido a la comunidad {comunidad.nombre}.")
        
        return redirect("comunidad:comunidad_detalle", comunidad_id=comunidad_id)

    # Solo mostrar mensajes si es miembro
    mensajes = []
    if es_miembro:
        mensajes = Mensaje.objects.filter(comunidad=comunidad).order_by("-timestamp")
        mensajes = list(mensajes)  # Convertir a lista para evitar problemas de queryset en el template

    context = {
        'comunidad': comunidad,
        'mensajes': mensajes,
        'es_miembro': es_miembro,
        'es_creador': comunidad.creador == request.user,
    }
    return render(request, "foro/comunidad_detalle.html", context)

@login_required
def unirse_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    if request.method == 'POST':
        if not MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists():
            MiembroComunidad.objects.create(usuario=request.user, comunidad=comunidad)
            messages.success(request, f"Te has unido a la comunidad {comunidad.nombre}.")
        else:
            messages.info(request, "Ya eres miembro de esta comunidad.")
    return redirect('comunidad_detalle', comunidad_id=comunidad.id)

@login_required
def salir_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).first()
    
    if miembro:
        miembro.delete()
        messages.success(request, f"Has salido de {comunidad.nombre}.")
    
    return redirect('comunidades_home')

@login_required
def zona_descanso(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Verificar que el usuario sea miembro
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    if not es_miembro:
        messages.error(request, "Debes ser miembro de la comunidad para acceder a la zona de descanso.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    miembros_activos = comunidad.get_miembros_activos()
    miembros_inactivos = comunidad.get_miembros_inactivos()
    
    context = {
        'comunidad': comunidad,
        'miembros_activos': miembros_activos,
        'miembros_inactivos': miembros_inactivos,
        'es_creador': comunidad.creador == request.user,
    }
    return render(request, "foro/zona_descanso.html", context)

@login_required
def buscar_comunidades(request):
    query = request.GET.get("q", "")
    resultados = []
    
    if query:
        resultados = Comunidad.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query),
            activa=True
        ).order_by('-es_destacada', '-fecha_creacion')
    
    return render(request, "foro/buscar_comunidades.html", {
        "resultados": resultados,
        "query": query
    })

@login_required
def unirse_por_invitacion(request, codigo_invitacion):
    comunidad = get_object_or_404(Comunidad, codigo_invitacion=codigo_invitacion, activa=True)
    
    if not MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists():
        MiembroComunidad.objects.create(usuario=request.user, comunidad=comunidad)
        messages.success(request, f"Te has unido exitosamente a {comunidad.nombre} por invitación.")
    else:
        messages.info(request, "Ya eres miembro de esta comunidad.")
    
    return redirect('comunidad_detalle', comunidad_id=comunidad.id)

@login_required
def reportar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion')
        
        if motivo and descripcion:
            Reporte.objects.create(
                comunidad=comunidad,
                reportado_por=request.user,
                motivo=motivo,
                descripcion=descripcion
            )
            messages.success(request, "Reporte enviado exitosamente.")
        else:
            messages.error(request, "Por favor completa todos los campos.")
        
        return redirect('zona_descanso', comunidad_id=comunidad_id)
    
    return render(request, "foro/reportar.html", {'comunidad': comunidad})

@login_required
def asistente_ia(request):
    if request.method == 'POST':
        pregunta = request.POST.get('pregunta', '').strip()
        try:
            response = requests.post(
                "http://localhost:8001/api/responder",
                json={"pregunta": pregunta},
                timeout=10
            )
            respuesta = response.json().get("respuesta", "No se recibió respuesta.")
        except Exception as e:
            respuesta = "Ocurrió un error al conectar con la API externa."

        return JsonResponse({'respuesta': respuesta})
    return render(request, "foro/asistente_ia.html")

@login_required
def unirse_a_conversacion(request, comunidad_id):
    """Permite a un usuario unirse a una comunidad y acceder al chat"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar si ya es miembro
    es_miembro = MiembroComunidad.objects.filter(
        usuario=request.user, 
        comunidad=comunidad
    ).exists()
    
    if not es_miembro:
        # Crear membresía
        MiembroComunidad.objects.create(
            usuario=request.user,
            comunidad=comunidad,
            estado='activo',
            rol='estudiante'  # Por defecto estudiante
        )
        
        # Crear mensaje de sistema
        Mensaje.objects.create(
            comunidad=comunidad,
            autor=request.user,
            perfil=request.user.perfil,  # si tienes `Perfil` con OneToOneField
            contenido=f"{Perfil.get_full_name() or request.user.username} se ha unido a la comunidad",  
            tipo='sistema'
        )
        
        messages.success(request, f"¡Te has unido exitosamente a {comunidad.nombre}!")
    else:
        messages.info(request, "Ya eres miembro de esta comunidad")
    
    return redirect('comunidad:comunidad_detalle', comunidad_id=comunidad_id)
    
@login_required
def mis_comunidades(request):
    """Vista para mostrar las comunidades del usuario"""
    mis_comunidades = Comunidad.objects.filter(
        miembros=request.user,
        activa=True
    ).order_by('-fecha_creacion')
    
    return render(request, "foro/mis_comunidades.html", {
        'comunidades': mis_comunidades
    })
from django.shortcuts import redirect

@login_required
def verificar_nombre_comunidad(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre', '')
        existe = Comunidad.objects.filter(nombre=nombre).exists()
        return JsonResponse({'disponible': not existe})
    return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@login_required
def gestionar_miembros(request, comunidad_id):
    """Vista para gestionar miembros de la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Solo el creador puede gestionar miembros
    if comunidad.creador != request.user:
        messages.error(request, "No tienes permisos para gestionar esta comunidad.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    miembros = MiembroComunidad.objects.filter(comunidad=comunidad)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        miembro_id = request.POST.get('miembro_id')
        
        try:
            miembro = MiembroComunidad.objects.get(id=miembro_id, comunidad=comunidad)
            
            if accion == 'cambiar_estado':
                miembro.estado = 'inactivo' if miembro.estado == 'activo' else 'activo'
                miembro.save()
                messages.success(request, f"Estado de {miembro.usuario.username} actualizado")
            elif accion == 'cambiar_rol':
                miembro.rol = 'profesor' if miembro.rol == 'estudiante' else 'estudiante'
                miembro.save()
                messages.success(request, f"Rol de {miembro.usuario.username} actualizado")
            elif accion == 'expulsar':
                if miembro.usuario != request.user:  # No puede expulsarse a sí mismo
                    miembro.delete()
                    messages.success(request, f"{miembro.usuario.username} ha sido expulsado de la comunidad")
                    
        except MiembroComunidad.DoesNotExist:
            messages.error(request, "Miembro no encontrado")
    
    return render(request, "foro/gestionar_miembros.html", {
        'comunidad': comunidad,
        'miembros': miembros
    })

@login_required
def compartir_comunidad(request, comunidad_id):
    """Vista para compartir el código de invitación de la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Solo miembros pueden ver el código
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    if not es_miembro:
        messages.error(request, "No tienes permisos para acceder a esta información.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    # Generar URL de invitación
    url_invitacion = request.build_absolute_uri(
        f"/comunidad/invitacion/{comunidad.codigo_invitacion}/"
    )
    
    return render(request, "foro/compartir_comunidad.html", {
        'comunidad': comunidad,
        'url_invitacion': url_invitacion
    })
@login_required
def obtener_mensajes(request, comunidad_id):
    """Obtiene los mensajes más recientes de la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar que sea miembro
    if not MiembroComunidad.objects.filter(
        usuario=request.user, 
        comunidad=comunidad, 
        estado='activo'
    ).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener ID del último mensaje recibido
    ultimo_id = request.GET.get('ultimo_id', 0)
    
    # Obtener mensajes nuevos
    mensajes = Mensaje.objects.filter(
        comunidad=comunidad,
        id__gt=ultimo_id
    ).select_related('autor').order_by('timestamp')
    
    mensajes_data = []
    for mensaje in mensajes:
        mensajes_data.append({
            'id': mensaje.id,
            'autor': mensaje.autor.get_full_name() or mensaje.autor.get_username,
            'contenido': mensaje.contenido,
            'timestamp': mensaje.timestamp.strftime('%d/%m/%Y %H:%M'),
            'es_autor': mensaje.autor == request.user,
            'tipo': mensaje.tipo,
            'es_importante': mensaje.es_importante
        })
    
    return JsonResponse({
        'mensajes': mensajes_data,
        'hay_nuevos': len(mensajes_data) > 0
    })

@login_required
def enviar_mensaje(request, comunidad_id):
    """Envía un mensaje a la comunidad"""
    if request.method == 'POST':
        comunidad = get_object_or_404(Comunidad, id=comunidad_id)
        
        # Verificar que sea miembro
        if not MiembroComunidad.objects.filter(
            usuario=request.user, 
            comunidad=comunidad, 
            estado='activo'
        ).exists():
            return JsonResponse({'error': 'No eres miembro de esta comunidad'}, status=403)
        
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            mensaje = Mensaje.objects.create(
                comunidad=comunidad,
                autor=request.user,
                contenido=contenido,
                tipo='publico'
            )
            
            # Guardar en historial
            HistorialMensajes.objects.create(
                usuario=request.user,
                comunidad=comunidad,
                contenido=contenido,
                tipo_mensaje='publico'
            )
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'mensaje': {
                        'id': mensaje.id,
                        'autor': mensaje.autor.get_full_name() or mensaje.autor.username,
                        'contenido': mensaje.contenido,
                        'timestamp': mensaje.timestamp.strftime('%d/%m/%Y %H:%M'),
                        'es_autor': mensaje.autor == request.user
                    }
                })
    
    return redirect('comunidad:comunidad_detalle', comunidad_id=comunidad_id)

@login_required
def enviar_mensaje_privado(request, comunidad_id):
    """Envía un mensaje privado a otro miembro de la comunidad"""
    if request.method == 'POST':
        comunidad = get_object_or_404(Comunidad, id=comunidad_id)
        
        # Verificar que sea miembro
        if not MiembroComunidad.objects.filter(
            usuario=request.user, 
            comunidad=comunidad, 
            estado='activo'
        ).exists():
            return JsonResponse({'error': 'No eres miembro de esta comunidad'}, status=403)
        
        destinatario_id = request.POST.get('destinatario_id')
        contenido = request.POST.get('contenido', '').strip()
        
        if not destinatario_id or not contenido:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        # Verificar que el destinatario sea miembro
        try:
            destinatario = MiembroComunidad.objects.get(
                usuario_id=destinatario_id,
                comunidad=comunidad,
                estado='activo'
            ).usuario
        except MiembroComunidad.DoesNotExist:
            return JsonResponse({'error': 'Destinatario no válido'}, status=400)
        
        # Crear mensaje privado
        mensaje_privado = MensajePrivado.objects.create(
            comunidad=comunidad,
            remitente=request.user,
            destinatario=destinatario,
            contenido=contenido
        )
        
        # Guardar en historial
        HistorialMensajes.objects.create(
            usuario=request.user,
            comunidad=comunidad,
            contenido=contenido,
            tipo_mensaje='privado',
            destinatario=destinatario
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Mensaje privado enviado correctamente'
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def obtener_mensajes_privados(request, comunidad_id, usuario_id):
    """Obtiene la conversación privada con otro usuario"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar que sea miembro
    if not MiembroComunidad.objects.filter(
        usuario=request.user, 
        comunidad=comunidad, 
        estado='activo'
    ).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener mensajes privados entre los dos usuarios
    mensajes = MensajePrivado.objects.filter(
        comunidad=comunidad
    ).filter(
        Q(remitente=request.user, destinatario_id=usuario_id) |
        Q(remitente_id=usuario_id, destinatario=request.user)
    ).select_related('remitente', 'destinatario').order_by('timestamp')
    
    # Marcar mensajes como leídos
    MensajePrivado.objects.filter(
        comunidad=comunidad,
        remitente_id=usuario_id,
        destinatario=request.user,
        leido=False
    ).update(leido=True, fecha_lectura=timezone.now())
    
    mensajes_data = []
    for mensaje in mensajes:
        mensajes_data.append({
            'id': mensaje.id,
            'remitente': mensaje.remitente.get_full_name() or mensaje.remitente.username,
            'contenido': mensaje.contenido,
            'timestamp': mensaje.timestamp.strftime('%d/%m/%Y %H:%M'),
            'es_mio': mensaje.remitente == request.user,
            'leido': mensaje.leido
        })
    
    return JsonResponse({'mensajes': mensajes_data})

@login_required
def obtener_miembros_en_linea(request, comunidad_id):
    """Obtiene la lista de miembros en línea"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar que sea miembro
    if not MiembroComunidad.objects.filter(
        usuario=request.user, 
        comunidad=comunidad, 
        estado='activo'
    ).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener miembros activos de los últimos 10 minutos
    tiempo_limite = timezone.now() - timezone.timedelta(minutes=10)
    
    miembros_activos = MiembroComunidad.objects.filter(
        comunidad=comunidad,
        estado='activo',
        ultima_conexion__gte=tiempo_limite
    ).select_related('usuario', 'usuario__perfil')
    
    miembros_data = []
    for miembro in miembros_activos:
        miembros_data.append({
            'id': miembro.usuario.id,
            'nombre': miembro.usuario.get_full_name() or miembro.usuario.username,
            'rol': miembro.get_rol_display(),
            'es_yo': miembro.usuario == request.user,
            'avatar': miembro.usuario.perfil.avatar.url if hasattr(miembro.usuario, 'perfil') else None
        })
    
    return JsonResponse({'miembros': miembros_data})

@login_required
def actualizar_estado_conexion(request, comunidad_id):
    """Actualiza el estado de conexión del usuario"""
    if request.method == 'POST':
        comunidad = get_object_or_404(Comunidad, id=comunidad_id)
        
        # Verificar que sea miembro
        miembro = MiembroComunidad.objects.filter(
            usuario=request.user, 
            comunidad=comunidad, 
            estado='activo'
        ).first()
        
        if not miembro:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        # Actualizar última conexión
        miembro.ultima_conexion = timezone.now()
        miembro.en_linea = True
        miembro.save()
        
        # Crear o actualizar conexión
        ConexionUsuario.objects.update_or_create(
            usuario=request.user,
            comunidad=comunidad,
            session_key=request.session.session_key,
            defaults={
                'activa': True,
                'timestamp_desconexion': None
            }
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def recuperar_mensajes_historial(request, comunidad_id):
    """Recupera mensajes del historial para el usuario"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar que sea miembro
    if not MiembroComunidad.objects.filter(
        usuario=request.user, 
        comunidad=comunidad, 
        estado='activo'
    ).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener mensajes del historial del usuario
    historial = HistorialMensajes.objects.filter(
        usuario=request.user,
        comunidad=comunidad,
        fecha_expiracion__gt=timezone.now()
    ).order_by('-timestamp')[:50]  # Últimos 50 mensajes
    
    mensajes_data = []
    for mensaje in historial:
        mensajes_data.append({
            'contenido': mensaje.contenido,
            'timestamp': mensaje.timestamp.strftime('%d/%m/%Y %H:%M'),
            'tipo': mensaje.tipo_mensaje,
            'destinatario': mensaje.destinatario.get_full_name() if mensaje.destinatario else None
        })
    
    return JsonResponse({'historial': mensajes_data})

# Función auxiliar para limpiar conexiones inactivas
def limpiar_conexiones_inactivas():
    """Limpia las conexiones que han estado inactivas por más de 10 minutos"""
    tiempo_limite = timezone.now() - timezone.timedelta(minutes=10)
    
    # Marcar conexiones como inactivas
    ConexionUsuario.objects.filter(
        timestamp_conexion__lt=tiempo_limite,
        activa=True,
        timestamp_desconexion__isnull=True
    ).update(
        activa=False,
        timestamp_desconexion=timezone.now()
    )
    
    # Actualizar estado de miembros
    MiembroComunidad.objects.filter(
        ultima_conexion__lt=tiempo_limite,
        en_linea=True
    ).update(en_linea=False)

def unirse_comunidad(request, codigo_invitacion):
    """Vista para que los usuarios se unan a una comunidad usando el código"""
    try:
        comunidad = get_object_or_404(Comunidad, codigo_invitacion=codigo_invitacion, activa=True)
    except:
        messages.error(request, 'Código de invitación inválido o comunidad no activa.')
        return redirect('lista_comunidades')
    
    if not request.user.is_authenticated:
        messages.info(request, f'Debes iniciar sesión para unirte a "{comunidad.nombre}".')
        # Guardar el código en la sesión para después del login
        request.session['codigo_invitacion_pendiente'] = codigo_invitacion
        return redirect('login')
    
    # Verificar si ya es miembro
    if MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists():
        messages.info(request, f'Ya eres miembro de "{comunidad.nombre}".')
        return redirect('detalle_comunidad', comunidad_id=comunidad.id)
    
    if request.method == 'POST':
        # Procesar unión a la comunidad
        try:
            with transaction.atomic():
                # Crear membresía
                MiembroComunidad.objects.create(
                    usuario=request.user,
                    comunidad=comunidad,
                    rol='estudiante',
                    estado='activo'
                )
                
                # Marcar invitación como procesada si existe
                Invitacion.objects.filter(
                    comunidad=comunidad,
                    invitado=request.user,
                    procesada=False
                ).update(aceptada=True, procesada=True)
                
                messages.success(
                    request,
                    f'¡Te has unido exitosamente a "{comunidad.nombre}"!'
                )
                return redirect('detalle_comunidad', comunidad_id=comunidad.id)
                
        except Exception as e:
            messages.error(request, f'Error al unirse a la comunidad: {str(e)}')
    
    # Mostrar página de confirmación
    context = {
        'comunidad': comunidad,
        'miembros_count': comunidad.get_miembros_activos().count(),
    }
    return render(request, 'foro/unirse_comunidad.html', context)

@login_required
def invitar_estudiantes(request, comunidad_id):
    """Vista principal para mostrar las opciones de invitación"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar que el usuario sea profesor o creador de la comunidad
    try:
        miembro = MiembroComunidad.objects.get(usuario=request.user, comunidad=comunidad)
        if miembro.rol != 'profesor' and comunidad.creador != request.user:
            messages.error(request, 'No tienes permisos para invitar estudiantes a esta comunidad.')
            return redirect('detalle_comunidad', comunidad_id=comunidad.id)
    except MiembroComunidad.DoesNotExist:
        if comunidad.creador != request.user:
            messages.error(request, 'No eres miembro de esta comunidad.')
            return redirect('lista_comunidades')
    
    # Contar invitaciones pendientes
    invitaciones_pendientes = Invitacion.objects.filter(
        comunidad=comunidad, 
        procesada=False
    ).count()
    
    # Crear enlaces para compartir
    enlace_base = request.build_absolute_uri(
        reverse('comunidad:unirse_por_invitacion', args=[comunidad.codigo_invitacion])
    )
    
    # Mensajes para compartir
    mensaje_whatsapp = f"¡Únete a nuestra comunidad educativa '{comunidad.nombre}'! Usa este enlace: {enlace_base}"
    mensaje_email = f"""
Hola,

Has sido invitado/a a unirte a la comunidad educativa '{comunidad.nombre}'.

{comunidad.descripcion}

Para unirte, haz clic en el siguiente enlace:
{enlace_base}

O usa el código de invitación: {comunidad.codigo_invitacion}

¡Esperamos verte pronto!
    """.strip()
    
    context = {
        'comunidad': comunidad,
        'invitaciones_pendientes': invitaciones_pendientes,
        'enlace_whatsapp': quote(mensaje_whatsapp),
        'enlace_email': quote(mensaje_email),
    }
    
    return render(request, 'foro/invitar_estudiantes.html', context)

@login_required
def regenerar_codigo(request, comunidad_id):
    """Vista para regenerar el código de invitación"""
    if request.method != 'POST':
        return redirect('invitar_estudiantes', comunidad_id=comunidad_id)
    
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar permisos
    try:
        miembro = MiembroComunidad.objects.get(usuario=request.user, comunidad=comunidad)
        if miembro.rol != 'profesor' and comunidad.creador != request.user:
            messages.error(request, 'No tienes permisos para regenerar el código.')
            return redirect('detalle_comunidad', comunidad_id=comunidad.id)
    except MiembroComunidad.DoesNotExist:
        if comunidad.creador != request.user:
            messages.error(request, 'No eres miembro de esta comunidad.')
            return redirect('lista_comunidades')
    
    # Generar nuevo código único
    nuevo_codigo = str(uuid.uuid4())[:8].upper()
    while Comunidad.objects.filter(codigo_invitacion=nuevo_codigo).exists():
        nuevo_codigo = str(uuid.uuid4())[:8].upper()
    
    codigo_anterior = comunidad.codigo_invitacion
    comunidad.codigo_invitacion = nuevo_codigo
    comunidad.save()
    
    messages.success(
        request, 
        f'Código de invitación regenerado exitosamente. '
        f'Código anterior ({codigo_anterior}) ya no es válido.'
    )
    
    return redirect('invitar_estudiantes', comunidad_id=comunidad.id)

@login_required
def enviar_invitaciones_email(request, comunidad_id):
    """Vista para enviar invitaciones por email"""
    if request.method != 'POST':
        return redirect('invitar_estudiantes', comunidad_id=comunidad_id)
    
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Verificar permisos
    try:
        miembro = MiembroComunidad.objects.get(usuario=request.user, comunidad=comunidad)
        if miembro.rol != 'profesor' and comunidad.creador != request.user:
            messages.error(request, 'No tienes permisos para enviar invitaciones.')
            return redirect('detalle_comunidad', comunidad_id=comunidad.id)
    except MiembroComunidad.DoesNotExist:
        if comunidad.creador != request.user:
            messages.error(request, 'No eres miembro de esta comunidad.')
            return redirect('lista_comunidades')
    
    emails_raw = request.POST.get('emails', '').strip()
    mensaje_personalizado = request.POST.get('mensaje_personalizado', '').strip()
    
    if not emails_raw:
        messages.error(request, 'Debes ingresar al menos un email.')
        return redirect('invitar_estudiantes', comunidad_id=comunidad.id)
    
    # Procesar emails
    emails_list = []
    for email in re.split(r'[,\n]', emails_raw):
        email = email.strip()
        if email:
            try:
                validate_email(email)
                emails_list.append(email)
            except ValidationError:
                messages.error(request, f'Email inválido: {email}')
                return redirect('invitar_estudiantes', comunidad_id=comunidad.id)
    
    if not emails_list:
        messages.error(request, 'No se encontraron emails válidos.')
        return redirect('invitar_estudiantes', comunidad_id=comunidad.id)
    
    # Enviar invitaciones
    invitaciones_enviadas = 0
    invitaciones_existentes = 0
    errores = []
    
    enlace_invitacion = request.build_absolute_uri(
        reverse('unirse_comunidad', args=[comunidad.codigo_invitacion])
    )
    
    for email in emails_list:
        try:
            # Verificar si el usuario ya existe
            try:
                usuario_existente = User.objects.get(email=email)
                # Verificar si ya es miembro de la comunidad
                if MiembroComunidad.objects.filter(usuario=usuario_existente, comunidad=comunidad).exists():
                    invitaciones_existentes += 1
                    continue
                
                # Verificar si ya tiene una invitación pendiente
                if Invitacion.objects.filter(comunidad=comunidad, invitado=usuario_existente, procesada=False).exists():
                    invitaciones_existentes += 1
                    continue
                
                # Crear invitación para usuario existente
                with transaction.atomic():
                    invitacion = Invitacion.objects.create(
                        comunidad=comunidad,
                        invitado_por=request.user,
                        invitado=usuario_existente
                    )
                    
                    # Enviar email
                    enviar_email_invitacion_usuario_existente(
                        invitacion, enlace_invitacion, mensaje_personalizado
                    )
                    invitaciones_enviadas += 1
                    
            except User.DoesNotExist:
                # Usuario no existe, enviar invitación general
                enviar_email_invitacion_nuevo_usuario(
                    email, comunidad, request.user, enlace_invitacion, mensaje_personalizado
                )
                invitaciones_enviadas += 1
                
        except Exception as e:
            errores.append(f'Error enviando a {email}: {str(e)}')
    
    # Mostrar resultados
    if invitaciones_enviadas > 0:
        messages.success(
            request, 
            f'Se enviaron {invitaciones_enviadas} invitaciones exitosamente.'
        )
    
    if invitaciones_existentes > 0:
        messages.info(
            request,
            f'{invitaciones_existentes} usuarios ya son miembros o tienen invitaciones pendientes.'
        )
    
    if errores:
        for error in errores:
            messages.error(request, error)
    
    return redirect('invitar_estudiantes', comunidad_id=comunidad.id)

def enviar_email_invitacion_usuario_existente(invitacion, enlace_invitacion, mensaje_personalizado):
    """Envía email de invitación a usuario existente"""
    context = {
        'invitacion': invitacion,
        'comunidad': invitacion.comunidad,
        'invitado_por': invitacion.invitado_por,
        'enlace_invitacion': enlace_invitacion,
        'mensaje_personalizado': mensaje_personalizado,
    }
    
    # Renderizar template del email
    subject = f'Invitación a la comunidad {invitacion.comunidad.nombre}'
    html_message = render_to_string('M6_Comunidades/emails/invitacion_usuario_existente.html', context)
    plain_message = render_to_string('M6_Comunidades/emails/invitacion_usuario_existente.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitacion.invitado.email],
        fail_silently=False,
    )

def enviar_email_invitacion_nuevo_usuario(email, comunidad, invitado_por, enlace_invitacion, mensaje_personalizado):
    """Envía email de invitación a usuario que no está registrado"""
    context = {
        'email': email,
        'comunidad': comunidad,
        'invitado_por': invitado_por,
        'enlace_invitacion': enlace_invitacion,
        'mensaje_personalizado': mensaje_personalizado,
        'enlace_registro': f"{enlace_invitacion}?registro=true",
    }
    
    subject = f'Invitación a la comunidad {comunidad.nombre}'
    html_message = render_to_string('M6_Comunidades/emails/invitacion_nuevo_usuario.html', context)
    plain_message = render_to_string('M6_Comunidades/emails/invitacion_nuevo_usuario.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

# Vista adicional para manejar el login con código pendiente
def procesar_codigo_pendiente(request):
    """Procesa código de invitación después del login"""
    if request.user.is_authenticated and 'codigo_invitacion_pendiente' in request.session:
        codigo = request.session.pop('codigo_invitacion_pendiente')
        return redirect('unirse_comunidad', codigo_invitacion=codigo)
    return redirect('lista_comunidades')