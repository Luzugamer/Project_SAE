from django.db import models
from Login.models import Usuario
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
from django.utils import timezone
import os

# Lista de países ordenados alfabéticamente
PAISES_CHOICES = [
    ('AF', 'Afganistán'),
    ('AL', 'Albania'),
    ('DE', 'Alemania'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AG', 'Antigua y Barbuda'),
    ('SA', 'Arabia Saudita'),
    ('DZ', 'Argelia'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaiyán'),
    ('BS', 'Bahamas'),
    ('BD', 'Bangladés'),
    ('BB', 'Barbados'),
    ('BH', 'Baréin'),
    ('BE', 'Bélgica'),
    ('BZ', 'Belice'),
    ('BJ', 'Benín'),
    ('BY', 'Bielorrusia'),
    ('BO', 'Bolivia'),
    ('BA', 'Bosnia y Herzegovina'),
    ('BW', 'Botsuana'),
    ('BR', 'Brasil'),
    ('BN', 'Brunéi'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('BT', 'Bután'),
    ('CV', 'Cabo Verde'),
    ('KH', 'Camboya'),
    ('CM', 'Camerún'),
    ('CA', 'Canadá'),
    ('QA', 'Catar'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CY', 'Chipre'),
    ('VA', 'Ciudad del Vaticano'),
    ('CO', 'Colombia'),
    ('KM', 'Comoras'),
    ('CG', 'Congo'),
    ('KP', 'Corea del Norte'),
    ('KR', 'Corea del Sur'),
    ('CI', 'Costa de Marfil'),
    ('CR', 'Costa Rica'),
    ('HR', 'Croacia'),
    ('CU', 'Cuba'),
    ('DK', 'Dinamarca'),
    ('DM', 'Dominica'),
    ('EC', 'Ecuador'),
    ('EG', 'Egipto'),
    ('SV', 'El Salvador'),
    ('AE', 'Emiratos Árabes Unidos'),
    ('ER', 'Eritrea'),
    ('SK', 'Eslovaquia'),
    ('SI', 'Eslovenia'),
    ('ES', 'España'),
    ('US', 'Estados Unidos'),
    ('EE', 'Estonia'),
    ('ET', 'Etiopía'),
    ('PH', 'Filipinas'),
    ('FI', 'Finlandia'),
    ('FJ', 'Fiyi'),
    ('FR', 'Francia'),
    ('GA', 'Gabón'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('GH', 'Ghana'),
    ('GD', 'Granada'),
    ('GR', 'Grecia'),
    ('GT', 'Guatemala'),
    ('GY', 'Guyana'),
    ('GN', 'Guinea'),
    ('GQ', 'Guinea Ecuatorial'),
    ('GW', 'Guinea-Bisáu'),
    ('HT', 'Haití'),
    ('HN', 'Honduras'),
    ('HU', 'Hungría'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IQ', 'Irak'),
    ('IR', 'Irán'),
    ('IE', 'Irlanda'),
    ('IS', 'Islandia'),
    ('IL', 'Israel'),
    ('IT', 'Italia'),
    ('JM', 'Jamaica'),
    ('JP', 'Japón'),
    ('JO', 'Jordán'),
    ('KZ', 'Kazajistán'),
    ('KE', 'Kenia'),
    ('KG', 'Kirguistán'),
    ('KI', 'Kiribati'),
    ('KW', 'Kuwait'),
    ('LA', 'Laos'),
    ('LS', 'Lesoto'),
    ('LV', 'Letonia'),
    ('LB', 'Líbano'),
    ('LR', 'Liberia'),
    ('LY', 'Libia'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lituania'),
    ('LU', 'Luxemburgo'),
    ('MK', 'Macedonia del Norte'),
    ('MG', 'Madagascar'),
    ('MY', 'Malasia'),
    ('MW', 'Malaui'),
    ('MV', 'Maldivas'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MA', 'Marruecos'),
    ('MU', 'Mauricio'),
    ('MR', 'Mauritania'),
    ('MX', 'México'),
    ('FM', 'Micronesia'),
    ('MD', 'Moldavia'),
    ('MC', 'Mónaco'),
    ('MN', 'Mongolia'),
    ('ME', 'Montenegro'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NI', 'Nicaragua'),
    ('NE', 'Níger'),
    ('NG', 'Nigeria'),
    ('NO', 'Noruega'),
    ('NZ', 'Nueva Zelanda'),
    ('OM', 'Omán'),
    ('NL', 'Países Bajos'),
    ('PK', 'Pakistán'),
    ('PW', 'Palaos'),
    ('PA', 'Panamá'),
    ('PG', 'Papúa Nueva Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Perú'),
    ('PL', 'Polonia'),
    ('PT', 'Portugal'),
    ('GB', 'Reino Unido'),
    ('CF', 'República Centroafricana'),
    ('CZ', 'República Checa'),
    ('CD', 'República Democrática del Congo'),
    ('DO', 'República Dominicana'),
    ('RW', 'Ruanda'),
    ('RO', 'Rumania'),
    ('RU', 'Rusia'),
    ('WS', 'Samoa'),
    ('KN', 'San Cristóbal y Nieves'),
    ('SM', 'San Marino'),
    ('VC', 'San Vicente y las Granadinas'),
    ('LC', 'Santa Lucía'),
    ('ST', 'Santo Tomé y Príncipe'),
    ('SN', 'Senegal'),
    ('RS', 'Serbia'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leona'),
    ('SG', 'Singapur'),
    ('SY', 'Siria'),
    ('SO', 'Somalia'),
    ('LK', 'Sri Lanka'),
    ('ZA', 'Sudáfrica'),
    ('SD', 'Sudán'),
    ('SS', 'Sudán del Sur'),
    ('SE', 'Suecia'),
    ('CH', 'Suiza'),
    ('SR', 'Surinam'),
    ('TH', 'Tailandia'),
    ('TZ', 'Tanzania'),
    ('TJ', 'Tayikistán'),
    ('TL', 'Timor Oriental'),
    ('TG', 'Togo'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad y Tobago'),
    ('TN', 'Túnez'),
    ('TM', 'Turkmenistán'),
    ('TR', 'Turquía'),
    ('TV', 'Tuvalu'),
    ('UA', 'Ucrania'),
    ('UG', 'Uganda'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistán'),
    ('VU', 'Vanuatu'),
    ('VE', 'Venezuela'),
    ('VN', 'Vietnam'),
    ('YE', 'Yemen'),
    ('DJ', 'Yibuti'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabue'),
]


class Universidad(models.Model):
    TIPO_SOLUCIONARIO_CHOICES = [
        ('admision', 'Solucionario de Examen de Admisión'),
        ('ejercicios', 'Solucionario de Ejercicios'),
        ('otro', 'Otro'),
    ]

    CURSOS_CHOICES = [
    ('MAT', 'Matemática'),
    ('COM', 'Comunicación'),
    ('CTA', 'Ciencia, Tecnología y Ambiente'),
    ('PER', 'Persona, Familia y Relaciones Humanas'),
    ('HIS', 'Historia'),
    ('GEO', 'Geografía'),
    ('CIV', 'Civismo'),
    ('RAZ', 'Razonamiento Verbal'),
    ('RM', 'Razonamiento Matemático'),
    ('TRI', 'Trigonometría'),
    ('ALG', 'Álgebra'),
    ('GEO2', 'Geometría'),
    ('ARI', 'Aritmética'),
    ('BIO', 'Biología'),
    ('QUI', 'Química'),
    ('FIS', 'Física'),
    ('ING', 'Inglés'),
    ('APT', 'Aptitud Académica'),
    ('OTR', 'Otro'),
    ]

    tipo_solucionario = models.CharField(max_length=50, choices=TIPO_SOLUCIONARIO_CHOICES, default='admision')
    curso = models.CharField(max_length=10, choices=CURSOS_CHOICES, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, choices=PAISES_CHOICES, blank=True, null=True)
    logo = models.ImageField(upload_to='logos_universidades/')
    codigo_modular = models.CharField(max_length=10, blank=True, null=True)
    institucion_educativa = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    distrito = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    profesor_creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)

    def get_pais_display(self):
        return dict(PAISES_CHOICES).get(self.pais, self.pais)

    def __str__(self):
        if self.institucion_educativa:
            return f"{self.nombre} ({self.institucion_educativa})"
        return self.nombre

    def clean(self):
        if self.tipo_solucionario == 'admision':
            if not self.pais or not self.nombre or not self.logo:
                raise ValidationError("Los campos 'país', 'nombre' y 'logo' son obligatorios para exámenes de admisión.")
        elif self.tipo_solucionario in ['ejercicios', 'otro']:
            if '-' not in self.nombre:
                raise ValidationError("El nombre del solucionario de ejercicios debe tener el formato: 'Curso - Tema'.")

    class Meta:
        unique_together = ('nombre', 'codigo_modular')
        ordering = ['nombre']


class Examen(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='examenes')
    nombre = models.CharField(max_length=255)
    fecha = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='examenes/', blank=True, null=True)
    miniatura = models.ImageField(upload_to='miniaturas_examenes/', blank=True, null=True)
    codigo_modular = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.fecha} ({self.universidad.nombre})"

    def clean(self):
        if self.archivo:
            if not self.archivo.name.endswith('.pdf'):
                raise ValidationError("Solo se permiten archivos PDF.")

    def generar_miniatura(self):
        if self.archivo and not self.miniatura:
            try:
                pdf_file = default_storage.open(self.archivo.name, 'rb')
                pdf_bytes = pdf_file.read()
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=70)
                if images:
                    img = images[0]
                    thumb_io = BytesIO()
                    img.thumbnail((200, 200))
                    img.save(thumb_io, format='JPEG', quality=85)
                    thumb_name = f"thumb_{os.path.basename(self.archivo.name)}.jpg"
                    self.miniatura.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                pdf_file.close()
                return True
            except Exception as e:
                print(f"Error generando miniatura: {e}")
                return False
        return False

    def save(self, *args, **kwargs):
        if not self.codigo_modular and self.universidad:
            self.codigo_modular = self.universidad.codigo_modular

        super().save(*args, **kwargs)

        if self.archivo and not self.miniatura:
            self.generar_miniatura()
            super().save(update_fields=["miniatura"])