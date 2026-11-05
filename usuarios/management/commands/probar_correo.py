"""
Prueba la configuración de correo del .env enviando un mensaje real.

    python manage.py probar_correo tu.correo@ejemplo.cl

Si falla, explica la causa más probable según el código que responde el servidor.
"""
import smtplib

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

AYUDA_MICROSOFT = {
    '5.7.139': (
        'Microsoft rechazó el inicio de sesión. Si la contraseña está bien, la causa es de la organización: '
        'tiene desactivado SMTP AUTH, exige MFA o bloquea la autenticación básica. Un alumno no puede cambiar '
        'eso; solo el área de TI de INACAP.'
    ),
    '5.7.30': 'Microsoft ya no acepta usuario y contraseña en esta cuenta (autenticación básica retirada).',
    '5.7.57': 'El servidor exige autenticarse: revisa EMAIL_HOST_USER, EMAIL_HOST_PASSWORD y EMAIL_USE_TLS.',
    '5.2.252': 'DEFAULT_FROM_EMAIL debe ser la misma dirección que EMAIL_HOST_USER.',
    '5.7.60': 'DEFAULT_FROM_EMAIL debe ser la misma dirección que EMAIL_HOST_USER.',
}


class Command(BaseCommand):
    help = 'Envía un correo de prueba con la configuración del .env.'

    def add_arguments(self, parser):
        parser.add_argument('destinatario')

    def handle(self, *args, **options):
        self.stdout.write(f'Backend:   {settings.EMAIL_BACKEND}')
        self.stdout.write(f'Servidor:  {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (TLS: {settings.EMAIL_USE_TLS})')
        self.stdout.write(f'Usuario:   {settings.EMAIL_HOST_USER or "(vacío)"}')
        self.stdout.write(f'Remitente: {settings.DEFAULT_FROM_EMAIL}')
        try:
            send_mail('Prueba de correo RODAMAR', 'Si lees esto, el correo está bien configurado.',
                      None, [options['destinatario']])
        except smtplib.SMTPException as error:
            detalle = str(error)
            for codigo, ayuda in AYUDA_MICROSOFT.items():
                if codigo in detalle:
                    raise CommandError(f'{detalle}\n\n{ayuda}')
            raise CommandError(f'El servidor rechazó el envío: {detalle}')
        except OSError as error:
            raise CommandError(
                f'No se pudo conectar con {settings.EMAIL_HOST}:{settings.EMAIL_PORT}: {error}\n'
                'Revisa EMAIL_HOST y EMAIL_PORT. Algunas redes bloquean el puerto 587.'
            )
        self.stdout.write(self.style.SUCCESS('El servidor aceptó el mensaje. Revisa la bandeja de entrada.'))
