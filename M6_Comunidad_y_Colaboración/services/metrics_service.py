from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import M6_Comunidad_y_Colaboración
from M6_Comunidad_y_Colaboración.models import Conversacion, Mensaje, ProblemaMatematico

class MetricsService:
    """
    Servicio para métricas y monitoreo del sistema
    """
    
    def obtener_estadisticas_generales(self):
        """
        Obtiene estadísticas generales del sistema
        """
        ahora = timezone.now()
        hace_24h = ahora - timedelta(hours=24)
        hace_7d = ahora - timedelta(days=7)
        
        return {
            'total_conversaciones': Conversacion.objects.count(),
            'conversaciones_24h': Conversacion.objects.filter(
                fecha_creacion__gte=hace_24h
            ).count(),
            'total_mensajes': Mensaje.objects.count(),
            'mensajes_ia_24h': Mensaje.objects.filter(
                tipo='ia',
                timestamp__gte=hace_24h
            ).count(),
            'problemas_resueltos': ProblemaMatematico.objects.filter(
                resuelto=True
            ).count(),
            'tiempo_respuesta_promedio': Mensaje.objects.filter(
                tipo='ia',
                tiempo_respuesta__isnull=False
            ).aggregate(Avg('tiempo_respuesta'))['tiempo_respuesta__avg'],
            'tokens_utilizados_7d': Mensaje.objects.filter(
                tipo='ia',
                timestamp__gte=hace_7d
            ).aggregate(Sum('tokens_utilizados'))['tokens_utilizados__sum'] or 0
        }
    
    def obtener_estadisticas_por_categoria(self):
        """
        Estadísticas por categoría matemática
        """
        return ProblemaMatematico.objects.values('categoria').annotate(
            total=Count('id'),
            resueltos=Count('id', filter=M6_Comunidad_y_Colaboración.models.Q(resuelto=True)),
            dificultad_promedio=Avg('dificultad')
        ).order_by('-total')
    
    def obtener_problemas_no_resueltos(self):
        """
        Problemas que no fueron resueltos exitosamente
        """
        return ProblemaMatematico.objects.filter(
            resuelto=False
        ).select_related('mensaje__conversacion').order_by('-mensaje__timestamp')[:20]