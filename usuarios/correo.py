"""
Confirmación del correo al crear una cuenta.

El enlace lleva un token firmado con la SECRET_KEY, que incluye el id de la
cuenta y su correo. No se guarda en la base de datos, vence solo y deja de
servir si el correo de la cuenta cambia.
"""
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from . import auditoria
from .models import RegistroAuditoria

logger = logging.getLogger(__name__)
_SALT = 'rodamar.confirmar-correo'


def crear_token(usuario):
    return signing.dumps({'id': usuario.pk, 'correo': usuario.email.lower()}, salt=_SALT)


def usuario_desde_token(token):
    """Devuelve el usuario del token, o None si es inválido, venció o ya no corresponde."""
    try:
        datos = signing.loads(token, salt=_SALT, max_age=settings.CONFIRMACION_CORREO_HORAS * 3600)
    except signing.BadSignature:  # SignatureExpired es una subclase
        return None
    usuario = User.objects.select_related('perfil').filter(pk=datos.get('id'), is_active=True).first()
    if usuario is None or usuario.email.lower() != datos.get('correo'):
        return None
    return usuario


def enviar_confirmacion(request, usuario):
    """
    Envía el enlace. Devuelve False si el envío falla: un servidor de correo
    caído o mal configurado no debe convertirse en un error 500 para el usuario.
    """
    enlace = request.build_absolute_uri(reverse('confirmar_correo', args=[crear_token(usuario)]))
    cuerpo = render_to_string('registration/confirmar_correo_email.txt', {
        'usuario': usuario, 'enlace': enlace, 'horas': settings.CONFIRMACION_CORREO_HORAS,
    })
    try:
        send_mail('Confirma tu cuenta en RODAMAR', cuerpo, None, [usuario.email])
    except Exception:
        logger.exception('No se pudo enviar el correo de confirmación a la cuenta %s', usuario.pk)
        return False
    return True


def marcar_confirmado(usuario, request=None):
    usuario.perfil.email_confirmado = True
    usuario.perfil.save(update_fields=['email_confirmado'])
    auditoria.registrar(
        RegistroAuditoria.CORREO_CONFIRMADO, request=request, actor=usuario, usuario_afectado=usuario,
        detalle=f'Correo: {usuario.email}',
    )
