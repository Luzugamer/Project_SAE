# Generated by Django 4.2.21 on 2025-07-04 04:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comunidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('icono', models.ImageField(blank=True, null=True, upload_to='iconos/')),
                ('institucion_afiliada', models.CharField(blank=True, max_length=200, null=True)),
                ('puntos_prestigio', models.IntegerField(default=0)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('es_destacada', models.BooleanField(default=False)),
                ('codigo_invitacion', models.CharField(blank=True, max_length=10, unique=True)),
                ('activa', models.BooleanField(default=True)),
                ('chat_activo', models.BooleanField(default=True)),
                ('notificaciones_email', models.BooleanField(default=True, help_text='Enviar notificaciones por email')),
                ('email_notificacion', models.EmailField(blank=True, help_text='Email personalizado para notificaciones (opcional)', max_length=254, null=True)),
                ('creador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comunidades_creadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Comunidades',
            },
        ),
        migrations.CreateModel(
            name='MensajeSala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('editado', models.BooleanField(default=False)),
                ('fecha_edicion', models.DateTimeField(blank=True, null=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ParticipanteSala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_union', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalaChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField(blank=True, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('solo_profesores', models.BooleanField(default=False)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salas_chat', to='M6_Comunidad_y_Colaboración.comunidad')),
                ('creada_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('participantes', models.ManyToManyField(related_name='salas_participando', through='M6_Comunidad_y_Colaboración.ParticipanteSala', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('comunidad', 'nombre')},
            },
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo', models.CharField(choices=[('spam', 'Spam'), ('contenido_inapropiado', 'Contenido inapropiado'), ('acoso', 'Acoso'), ('otro', 'Otro')], max_length=80)),
                ('descripcion', models.TextField()),
                ('fecha_reporte', models.DateTimeField(auto_now_add=True)),
                ('procesado', models.BooleanField(default=False)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.comunidad')),
                ('reportado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_chat', models.CharField(choices=[('disponible', 'Disponible'), ('ocupado', 'Ocupado'), ('ausente', 'Ausente'), ('no_molestar', 'No molestar')], default='disponible', max_length=20)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='participantesala',
            name='sala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.salachat'),
        ),
        migrations.AddField(
            model_name='participantesala',
            name='ultimo_mensaje_visto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='M6_Comunidad_y_Colaboración.mensajesala'),
        ),
        migrations.AddField(
            model_name='participantesala',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MiembroComunidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_union', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=10)),
                ('rol', models.CharField(choices=[('profesor', 'Profesor'), ('estudiante', 'Estudiante')], default='estudiante', max_length=10)),
                ('ultima_conexion', models.DateTimeField(auto_now=True)),
                ('en_linea', models.BooleanField(default=False)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.comunidad')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario', 'comunidad')},
            },
        ),
        migrations.AddField(
            model_name='mensajesala',
            name='sala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='M6_Comunidad_y_Colaboración.salachat'),
        ),
        migrations.CreateModel(
            name='MensajePrivado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('leido', models.BooleanField(default=False)),
                ('fecha_lectura', models.DateTimeField(blank=True, null=True)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_privados', to='M6_Comunidad_y_Colaboración.comunidad')),
                ('destinatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_recibidos', to=settings.AUTH_USER_MODEL)),
                ('remitente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_enviados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('es_importante', models.BooleanField(default=False)),
                ('tipo', models.CharField(choices=[('publico', 'Público'), ('privado', 'Privado'), ('sistema', 'Sistema')], default='publico', max_length=10)),
                ('editado', models.BooleanField(default=False)),
                ('fecha_edicion', models.DateTimeField(blank=True, null=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='M6_Comunidad_y_Colaboración.comunidad')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='HistorialMensajes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('tipo_mensaje', models.CharField(choices=[('publico', 'Público'), ('privado', 'Privado'), ('sistema', 'Sistema')], default='publico', max_length=10)),
                ('fecha_expiracion', models.DateTimeField()),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.comunidad')),
                ('destinatario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_recibidos_historial', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='comunidad',
            name='miembros',
            field=models.ManyToManyField(related_name='comunidades', through='M6_Comunidad_y_Colaboración.MiembroComunidad', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='participantesala',
            unique_together={('usuario', 'sala')},
        ),
        migrations.CreateModel(
            name='Invitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_invitacion', models.DateTimeField(auto_now_add=True)),
                ('aceptada', models.BooleanField(default=False)),
                ('procesada', models.BooleanField(default=False)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.comunidad')),
                ('invitado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitaciones_recibidas', to=settings.AUTH_USER_MODEL)),
                ('invitado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitaciones_enviadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('comunidad', 'invitado')},
            },
        ),
        migrations.CreateModel(
            name='ConexionUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40, unique=True)),
                ('timestamp_conexion', models.DateTimeField(auto_now_add=True)),
                ('timestamp_desconexion', models.DateTimeField(blank=True, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='M6_Comunidad_y_Colaboración.comunidad')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario', 'comunidad', 'session_key')},
            },
        ),
    ]
