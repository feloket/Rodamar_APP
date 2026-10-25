from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import auditoria
from .models import Perfil, RegistroAuditoria


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    """Todo usuario nuevo (registro, admin, createsuperuser) recibe su Perfil."""
    if created:
        Perfil.objects.get_or_create(usuario=instance)


@receiver(user_logged_in)
def auditar_login(sender, request, user, **kwargs):
    auditoria.registrar(RegistroAuditoria.LOGIN, request=request, actor=user, usuario_afectado=user)


@receiver(user_logged_out)
def auditar_logout(sender, request, user, **kwargs):
    if user is not None:
        auditoria.registrar(RegistroAuditoria.LOGOUT, request=request, actor=user, usuario_afectado=user)


@receiver(user_login_failed)
def auditar_login_fallido(sender, credentials, request=None, **kwargs):
    # Nunca se guarda la contraseña: solo el usuario que se intentó usar.
    intento = (credentials or {}).get('username', '')
    auditoria.registrar(
        RegistroAuditoria.LOGIN_FALLIDO, request=request, actor=None,
        usuario_texto=intento, detalle=f'Usuario ingresado: {intento}'[:255],
    )
