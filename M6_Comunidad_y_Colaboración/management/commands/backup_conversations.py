from django.core.management.base import BaseCommand
from django.core import serializers
from django.utils import timezone
from datetime import timedelta
import json
import os

from M6_Comunidad_y_Colaboración.models import Conversacion, Mensaje, ProblemaMatematico

class Command(BaseCommand):
    help = 'Backup de conversaciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días atrás para incluir en el backup'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='backup_conversations.json',
            help='Archivo de salida'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        output_file = options['output']
        
        fecha_limite = timezone.now() - timedelta(days=days)
        
        # Obtener conversaciones recientes
        conversaciones = Conversacion.objects.filter(
            fecha_creacion__gte=fecha_limite
        ).prefetch_related('mensajes__problemamatemático')
        
        backup_data = {
            'timestamp': timezone.now().isoformat(),
            'conversaciones': []
        }
        
        for conv in conversaciones:
            conv_data = {
                'session_id': conv.session_id,
                'fecha_creacion': conv.fecha_creacion.isoformat(),
                'activa': conv.activa,
                'mensajes': []
            }
            
            for mensaje in conv.mensajes.all():
                msg_data = {
                    'tipo': mensaje.tipo,
                    'contenido': mensaje.contenido,
                    'timestamp': mensaje.timestamp.isoformat(),
                    'tokens_utilizados': mensaje.tokens_utilizados,
                    'tiempo_respuesta': mensaje.tiempo_respuesta
                }
                
                # Agregar datos del problema si existe
                if hasattr(mensaje, 'problemamatemático'):
                    problema = mensaje.problemamatemático
                    msg_data['problema'] = {
                        'nivel': problema.nivel,
                        'categoria': problema.categoria,
                        'dificultad': problema.dificultad,
                        'resuelto': problema.resuelto
                    }
                
                conv_data['mensajes'].append(msg_data)
            
            backup_data['conversaciones'].append(conv_data)
        
        # Guardar backup
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Backup completado: {len(backup_data["conversaciones"])} conversaciones guardadas en {output_file}'
            )
        )