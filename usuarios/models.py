from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

# El proyecto sigue usando django.contrib.auth.User (el estándar de Django).
# Los roles se manejan con is_superuser + Grupos: ver usuarios/roles.py
#
#   - ADMIN    -> is_superuser=True / is_staff=True
#   - EMPLEADO -> grupo "Empleados"
#   - CLIENTE  -> grupo "Clientes"
#   - INVITADO -> visitante sin sesión (AnonymousUser), solo vistas públicas
#
# User no tiene campo de teléfono ni relación con la empresa cliente, por
# eso se agrega un Perfil con OneToOneField (se crea solo, ver signals.py).

validar_telefono = RegexValidator(
    regex=r'^\+?[0-9 ]{8,15}$',
    message='Ingresa un teléfono válido, por ejemplo +56 9 1234 5678.',
)


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    telefono = models.CharField(max_length=20, blank=True, validators=[validar_telefono])
    # Empresa cliente a la que pertenece la cuenta (solo rol CLIENTE).
    # La asigna un EMPLEADO o ADMIN; el cliente no puede cambiarla.
    empresa = models.ForeignKey(
        'logistica.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuentas',
        verbose_name='Empresa cliente',
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.usuario}'


class RegistroAuditoria(models.Model):
    """
    Bitácora de seguridad. Cada fila es inmutable: no se edita ni se borra
    desde la aplicación ni desde /admin/. Guarda quién hizo qué, a quién,
    cuándo, desde qué IP y qué valor tenía antes/después.
    """

    LOGIN = 'LOGIN'
    LOGIN_FALLIDO = 'LOGIN_FALLIDO'
    LOGOUT = 'LOGOUT'
    REGISTRO = 'REGISTRO'
    CREACION_CUENTA = 'CREACION_CUENTA'
    EDICION_PERFIL = 'EDICION_PERFIL'
    EDICION_CUENTA = 'EDICION_CUENTA'
    CAMBIO_ROL = 'CAMBIO_ROL'
    CAMBIO_PASSWORD = 'CAMBIO_PASSWORD'
    ELIMINACION_CUENTA = 'ELIMINACION_CUENTA'
    EDICION_EMPRESA = 'EDICION_EMPRESA'
    LOGIN_BLOQUEADO = 'LOGIN_BLOQUEADO'
    RESET_SOLICITADO = 'RESET_SOLICITADO'
    RESET_COMPLETADO = 'RESET_COMPLETADO'
    CREACION_REGISTRO = 'CREACION_REGISTRO'
    EDICION_REGISTRO = 'EDICION_REGISTRO'
    ELIMINACION_REGISTRO = 'ELIMINACION_REGISTRO'

    ACCIONES = [
        (LOGIN, 'Inicio de sesión'),
        (LOGIN_FALLIDO, 'Inicio de sesión fallido'),
        (LOGOUT, 'Cierre de sesión'),
        (REGISTRO, 'Registro de cliente'),
        (CREACION_CUENTA, 'Creación de cuenta'),
        (EDICION_PERFIL, 'Edición de datos propios'),
        (EDICION_CUENTA, 'Edición de cuenta por personal'),
        (CAMBIO_ROL, 'Cambio de rol'),
        (CAMBIO_PASSWORD, 'Cambio de contraseña'),
        (ELIMINACION_CUENTA, 'Eliminación de cuenta'),
        (EDICION_EMPRESA, 'Edición de empresa cliente'),
        (LOGIN_BLOQUEADO, 'Login bloqueado por intentos fallidos'),
        (RESET_SOLICITADO, 'Recuperación de contraseña solicitada'),
        (RESET_COMPLETADO, 'Contraseña restablecida por correo'),
        (CREACION_REGISTRO, 'Creación de registro (buque, camión, vehículo, empresa)'),
        (EDICION_REGISTRO, 'Edición de registro'),
        (ELIMINACION_REGISTRO, 'Eliminación de registro'),
    ]

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    accion = models.CharField(max_length=30, choices=ACCIONES, db_index=True)

    # Quién realizó la acción (null = sistema / visitante)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='auditorias_realizadas',
    )
    # Cuenta afectada. Se guarda además el username como texto para que el
    # registro siga siendo legible aunque la cuenta se elimine.
    usuario_afectado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='auditorias_recibidas',
    )
    usuario_afectado_texto = models.CharField('Usuario afectado', max_length=150, blank=True)

    objeto = models.CharField(max_length=200, blank=True, help_text='Otro registro afectado (ej. empresa).')
    campo = models.CharField(max_length=100, blank=True)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    detalle = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f'{self.fecha:%d-%m-%Y %H:%M} {self.get_accion_display()} ({self.usuario_afectado_texto})'
