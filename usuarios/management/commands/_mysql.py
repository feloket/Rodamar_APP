"""Utilidades compartidas por exportar_sql e importar_sql."""
import glob
import os
import shutil
import tempfile
from contextlib import contextmanager

from django.conf import settings
from django.core.management.base import CommandError

RUTAS_WINDOWS = [
    r'C:\Program Files\MySQL\MySQL Server *\bin',
    r'C:\Program Files\MariaDB *\bin',
    r'C:\xampp\mysql\bin',
    r'C:\wamp64\bin\mysql\mysql*\bin',
    r'C:\laragon\bin\mysql\mysql*\bin',
]


def buscar_programa(nombre):
    """Busca mysql o mysqldump en el PATH y en las carpetas típicas de Windows."""
    encontrado = shutil.which(nombre)
    if encontrado:
        return encontrado
    for patron in RUTAS_WINDOWS:
        for carpeta in sorted(glob.glob(patron), reverse=True):
            for extension in ('.exe', ''):
                ruta = os.path.join(carpeta, nombre + extension)
                if os.path.isfile(ruta):
                    return ruta
    raise CommandError(
        f'No encontré {nombre}. Agrega la carpeta "bin" de MySQL al PATH de Windows, normalmente '
        r'C:\Program Files\MySQL\MySQL Server 8.4\bin, y abre una terminal nueva.'
    )


@contextmanager
def archivo_credenciales():
    """
    Deja las credenciales del .env en un archivo temporal privado. Pasarlas en la
    línea de comandos las dejaría visibles en la lista de procesos del sistema.
    """
    db = settings.DATABASES['default']
    clave = (db['PASSWORD'] or '').replace('\\', '\\\\').replace('"', '\\"')
    descriptor, ruta = tempfile.mkstemp(suffix='.cnf')
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as archivo:
            archivo.write(
                '[client]\n'
                f'user="{db["USER"]}"\n'
                f'password="{clave}"\n'
                f'host="{db["HOST"] or "localhost"}"\n'
                f'port={db["PORT"] or 3306}\n'
                'default-character-set=utf8mb4\n'
            )
        yield ruta
    finally:
        os.remove(ruta)
