from django.db import models
from django.core.files.storage import default_storage
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
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

TIPO_SOLUCIONARIO_CHOICES = [
    ('admision', 'Solucionario de Examen de Admisión'),
    ('ejercicios', 'Solucionario de Ejercicios'),
    ('otro', 'Otro'),
]

class Universidad(models.Model):
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, choices=PAISES_CHOICES)
    logo = models.ImageField(upload_to='logos_universidades/')
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    tipo_solucionario = models.CharField(max_length=20, choices=TIPO_SOLUCIONARIO_CHOICES, default='admision')

    def get_pais_display(self):
        return dict(PAISES_CHOICES).get(self.pais, self.pais)

class Examen(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='examenes')
    nombre = models.CharField(max_length=255)
    fecha = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='examenes/', blank=True, null=True)
    miniatura = models.ImageField(upload_to='miniaturas_examenes/', blank=True, null=True)

    def generar_miniatura(self):
        if self.archivo and not self.miniatura:
            try:
                # Leer el PDF
                pdf_file = default_storage.open(self.archivo.name, 'rb')
                pdf_bytes = pdf_file.read()
                
                # Convertir primera página a imagen
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=70)
                if images:
                    img = images[0]
                    
                    # Crear miniatura
                    thumb_io = BytesIO()
                    img.thumbnail((200, 200))
                    img.save(thumb_io, format='JPEG', quality=85)
                    
                    # Guardar miniatura
                    thumb_name = f"thumb_{os.path.basename(self.archivo.name)}.jpg"
                    self.miniatura.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                    
                pdf_file.close()
                return True
            except Exception as e:
                print(f"Error generando miniatura: {e}")
                return False
        return False

    def save(self, *args, **kwargs):
        if not self.pk or 'archivo' in kwargs.get('update_fields', []):
            self.generar_miniatura()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
    
