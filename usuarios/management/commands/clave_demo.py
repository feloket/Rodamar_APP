"""
Reemplaza la contraseña de todas las cuentas *_demo de la base configurada.

    python manage.py clave_demo

Sirve al desplegar: la contraseña por defecto está publicada en el README, y en
un sitio público cualquiera podría entrar como administrador con ella.
"""
import getpass

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cambia la contraseña de todas las cuentas de demostración.'

    def add_arguments(self, parser):
        parser.add_argument('--clave', help='Si se omite, se pregunta sin mostrarla en pantalla')

    def handle(self, *args, **options):
        cuentas = User.objects.filter(username__endswith='_demo')
        if not cuentas.exists():
            raise CommandError('No hay cuentas de demostración en esta base.')
        clave = options['clave'] or getpass.getpass('Contraseña nueva para las cuentas demo: ')
        try:
            validate_password(clave)
        except ValidationError as error:
            raise CommandError(' '.join(error.messages))
        for cuenta in cuentas:
            cuenta.set_password(clave)
            cuenta.save(update_fields=['password'])
        self.stdout.write(self.style.SUCCESS(f'Contraseña actualizada en {cuentas.count()} cuentas.'))
