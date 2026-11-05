"""
Crea el archivo .env de este computador, preguntando lo necesario.

    python scripts/configurar_env.py

Genera una SECRET_KEY nueva. Las contraseñas no se muestran al escribirlas y
quedan solo en el .env, que git ignora.
"""
import getpass
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / '.env'


def preguntar(texto, defecto=''):
    respuesta = input(f'{texto}{f" [{defecto}]" if defecto else ""}: ').strip()
    return respuesta or defecto


def comillas(valor):
    """Entre comillas simples, para que #, $ y espacios se lean tal cual."""
    return "'" + valor.replace('\\', '\\\\').replace("'", "\\'") + "'"


def main():
    if ENV.exists() and preguntar('Ya existe un .env. ¿Reemplazarlo? (s/n)', 'n').lower() != 's':
        print('Cancelado. No se cambió nada.')
        return

    print('\n--- Base de datos MySQL ---')
    lineas = [
        f"SECRET_KEY={comillas(secrets.token_urlsafe(50))}",
        'DEBUG=True',
        'ALLOWED_HOSTS=localhost,127.0.0.1',
        '',
        f"DB_NAME={preguntar('Nombre de la base', 'rodamar_db')}",
        f"DB_USER={preguntar('Usuario', 'rodamar_user')}",
        f"DB_PASSWORD={comillas(getpass.getpass('Contraseña del usuario de MySQL: '))}",
        f"DB_HOST={preguntar('Servidor', 'localhost')}",
        f"DB_PORT={preguntar('Puerto', '3306')}",
        '',
    ]

    print('\n--- Correo ---')
    if preguntar('¿Enviar correos reales por SMTP? (s/n, n = se imprimen en la terminal)', 'n').lower() == 's':
        correo = preguntar('Correo que envía')
        lineas += [
            'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend',
            f"EMAIL_HOST={preguntar('Servidor SMTP', 'smtp.office365.com')}",
            f"EMAIL_PORT={preguntar('Puerto', '587')}",
            'EMAIL_USE_TLS=True',
            f'EMAIL_HOST_USER={correo}',
            f"EMAIL_HOST_PASSWORD={comillas(getpass.getpass('Contraseña del correo: '))}",
            f'DEFAULT_FROM_EMAIL="RODAMAR <{correo}>"',
        ]
    else:
        lineas += ['EMAIL_BACKEND=usuarios.correo_consola.EmailBackend']

    ENV.write_text('\n'.join(lineas) + '\n', encoding='utf-8')
    print(f'\nListo: {ENV}')


if __name__ == '__main__':
    main()
