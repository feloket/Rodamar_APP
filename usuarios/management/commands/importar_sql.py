"""
Carga un archivo .sql en la base de datos configurada en el .env.

    python manage.py importar_sql database/rodamar_demo.sql

La base debe existir (ver README). Sus tablas se REEMPLAZAN por las del archivo.
"""
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ._mysql import archivo_credenciales, buscar_programa


class Command(BaseCommand):
    help = 'Importa un archivo .sql usando el cliente mysql.'

    def add_arguments(self, parser):
        parser.add_argument('archivo')
        parser.add_argument('--si', action='store_true', help='No pedir confirmación')

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        if not archivo.is_file():
            raise CommandError(f'No existe el archivo {archivo}')
        programa = buscar_programa('mysql')
        nombre_bd = settings.DATABASES['default']['NAME']

        if not options['si']:
            respuesta = input(f'Se reemplazarán las tablas de "{nombre_bd}" con {archivo}. ¿Continuar? [s/N] ')
            if respuesta.strip().lower() not in ('s', 'si', 'sí'):
                self.stdout.write('Cancelado. No se cambió nada.')
                return

        with archivo_credenciales() as credenciales, open(archivo, 'rb') as entrada:
            resultado = subprocess.run(
                [programa, f'--defaults-extra-file={credenciales}', nombre_bd],
                stdin=entrada, capture_output=True,
            )
        if resultado.returncode != 0:
            raise CommandError(f'mysql falló:\n{resultado.stderr.decode("utf-8", "replace").strip()}')
        self.stdout.write(self.style.SUCCESS(f'{archivo} cargado en "{nombre_bd}".'))
