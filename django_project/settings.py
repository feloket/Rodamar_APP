from pathlib import Path
import os
from dotenv import load_dotenv
import pymysql

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables definidas en el archivo .env (no se sube a git)
load_dotenv(BASE_DIR / '.env')

# La SECRET_KEY se lee desde el entorno. Si no existe (por ejemplo, alguien
# clonó el repo y no creó su .env), Django avisa altiro en vez de arrancar
# con una clave vacía o insegura.
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "Falta SECRET_KEY. Crea un archivo .env en la raíz del proyecto "
        "(mira .env.example) con SECRET_KEY=tu_clave_generada."
    )

# DEBUG también sale del entorno, por defecto en False (modo producción)
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# Aplicaciones del proyecto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Tus Apps
    'pages',
    'logistica',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Rol del usuario disponible en todas las plantillas (navbar)
                'usuarios.context_processors.rol_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración Regional
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rutas de autenticación
LOGIN_URL = 'login'
# Sin ?next= cada rol va a su inicio (ver usuarios.views.url_inicio)
LOGIN_REDIRECT_URL = 'mis_vehiculos'
LOGOUT_REDIRECT_URL = 'home'

# Sesiones y cookies
SESSION_COOKIE_AGE = 60 * 60 * 8          # 8 horas (una jornada) si no marca "Recordarme"
SESSION_COOKIE_HTTPONLY = True            # JavaScript no puede leer la cookie de sesión
CSRF_COOKIE_HTTPONLY = True
# En producción (DEBUG=False) las cookies solo viajan por HTTPS
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Encabezados de seguridad (siempre activos, no afectan el desarrollo local)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Solo en producción (DEBUG=False): obliga HTTPS. Se pueden desactivar con
# SECURE_SSL_REDIRECT=False en el .env si se prueba sin certificado.
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Correo. Por defecto se usa el backend de CONSOLA: los correos (ej. el de
# recuperar contraseña) se imprimen en la terminal donde corre runserver y
# no salen del computador. Para enviar correos reales habría que configurar
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend + EMAIL_HOST, etc.
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'usuarios.correo_consola.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'RODAMAR <no-responder@rodamar.local>')

# El enlace para restablecer la contraseña vence en 1 hora (por defecto Django usa 3 días)
PASSWORD_RESET_TIMEOUT = 60 * 60

# Bloqueo de login por intentos fallidos (ver usuarios/seguridad.py)
LOGIN_MAX_INTENTOS_USUARIO = 5
LOGIN_MAX_INTENTOS_IP = 30
LOGIN_BLOQUEO_MINUTOS = 15

# Mensajes: Django usa la etiqueta "error", pero Bootstrap usa "danger"
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}
# Al correr "python manage.py test" se usa un hash rápido para que los tests
# no tarden minutos. NUNCA aplica al servidor normal (runserver / producción).
import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
