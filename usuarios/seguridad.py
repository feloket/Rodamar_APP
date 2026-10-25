"""
Bloqueo de inicio de sesión por intentos fallidos (protección contra fuerza bruta).

Usa los registros LOGIN_FALLIDO que ya guarda la auditoría, así que no
necesita tablas ni librerías extra. Reglas (configurables en settings.py):

  - LOGIN_MAX_INTENTOS_USUARIO fallos seguidos para un mismo usuario
    -> ese usuario queda bloqueado LOGIN_BLOQUEO_MINUTOS.
  - LOGIN_MAX_INTENTOS_IP fallos desde una misma IP (a cualquier usuario)
    -> esa IP queda bloqueada el mismo tiempo. El límite es más alto porque
    en un laboratorio o una oficina muchas personas comparten IP.

Un login exitoso o una contraseña restablecida "limpian" los fallos previos
del usuario. Mientras dura el bloqueo, ni siquiera la contraseña correcta
permite entrar (si no, el atacante sabría cuándo acertó).
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import RegistroAuditoria


def _config():
    return (
        getattr(settings, 'LOGIN_MAX_INTENTOS_USUARIO', 5),
        getattr(settings, 'LOGIN_MAX_INTENTOS_IP', 30),
        getattr(settings, 'LOGIN_BLOQUEO_MINUTOS', 15),
    )


def login_bloqueado(username, ip):
    """Devuelve (bloqueado: bool, minutos_de_bloqueo: int)."""
    max_usuario, max_ip, minutos = _config()
    ventana = timezone.now() - timedelta(minutes=minutos)
    registros = RegistroAuditoria.objects

    username = (username or '').strip()
    if username:
        ultimo_ok = registros.filter(
            accion__in=[RegistroAuditoria.LOGIN, RegistroAuditoria.RESET_COMPLETADO],
            usuario_afectado_texto__iexact=username,
        ).order_by('-fecha').values_list('fecha', flat=True).first()
        desde = max(ventana, ultimo_ok) if ultimo_ok else ventana
        fallos_usuario = registros.filter(
            accion=RegistroAuditoria.LOGIN_FALLIDO,
            usuario_afectado_texto__iexact=username,
            fecha__gt=desde,
        ).count()
        if fallos_usuario >= max_usuario:
            return True, minutos

    if ip:
        fallos_ip = registros.filter(
            accion=RegistroAuditoria.LOGIN_FALLIDO, ip=ip, fecha__gt=ventana,
        ).count()
        if fallos_ip >= max_ip:
            return True, minutos

    return False, 0
