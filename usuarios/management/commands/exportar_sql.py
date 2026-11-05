"""
Exporta la base de datos configurada en el .env a un archivo .sql.

    python manage.py exportar_sql
    python manage.py exportar_sql --salida database/mi_respaldo.sql

No incluye las sesiones abiertas. Sí incluye los usuarios y sus datos, así que
un respaldo con datos reales no se sube a git (database/*.sql está en .gitignore).
"""
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ._mysql import archivo_credenciales, buscar_programa


class Command(BaseCommand):
    help = 'Exporta la base de datos a un archivo .sql usando mysqldump.'

    def add_arguments(self, parser):
        parser.add_argument('--salida', help='Archivo de destino (por defecto database/respaldo_FECHA.sql)')

    def handle(self, *args, **options):
        programa = buscar_programa('mysqldump')
        nombre_bd = settings.DATABASES['default']['NAME']
        salida = Path(options['salida'] or settings.BASE_DIR / 'database' / f'respaldo_{datetime.now():%Y%m%d_%H%M}.sql')
        salida.parent.mkdir(parents=True, exist_ok=True)

        version = subprocess.run([programa, '--version'], capture_output=True, text=True).stdout
        comunes = ['--no-tablespaces', '--skip-comments']  # no-tablespaces: evita pedir el privilegio PROCESS
        if 'MariaDB' not in version:
            comunes.append('--set-gtid-purged=OFF')

        with archivo_credenciales() as credenciales, tempfile.TemporaryDirectory() as carpeta:
            base = [programa, f'--defaults-extra-file={credenciales}', *comunes]
            esquema = Path(carpeta) / 'esquema.sql'
            datos = Path(carpeta) / 'datos.sql'
            # --result-file y no ">": en PowerShell, ">" guarda en UTF-16 y el archivo queda inservible
            pasos = [
                [*base, '--no-data', f'--result-file={esquema}', nombre_bd],
                [*base, '--no-create-info', '--single-transaction',
                 f'--ignore-table={nombre_bd}.django_session', f'--result-file={datos}', nombre_bd],
            ]
            for comando in pasos:
                resultado = subprocess.run(comando, capture_output=True, text=True)
                if resultado.returncode != 0:
                    raise CommandError(f'mysqldump falló:\n{resultado.stderr.strip()}')
            with open(salida, 'wb') as destino:
                for parte in (esquema, datos):
                    with open(parte, 'rb') as origen:
                        shutil.copyfileobj(origen, destino)

        self.stdout.write(self.style.SUCCESS(f'Base "{nombre_bd}" exportada a {salida}'))
