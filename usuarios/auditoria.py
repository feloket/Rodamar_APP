"""Funciones para escribir en la bitácora de auditoría (RegistroAuditoria)."""
from .models import RegistroAuditoria


def obtener_ip(request):
    # Se usa REMOTE_ADDR y no X-Forwarded-For: ese encabezado lo puede
    # falsificar cualquiera si no hay un proxy de confianza delante.
    if request is None:
        return None
    return request.META.get('REMOTE_ADDR') or None


def registrar(accion, request=None, actor=None, usuario_afectado=None,
              campo='', valor_anterior='', valor_nuevo='', detalle='', objeto='',
              usuario_texto=None):
    """Crea un registro de auditoría. Devuelve el registro creado."""
    if actor is None and request is not None and request.user.is_authenticated:
        actor = request.user
    return RegistroAuditoria.objects.create(
        accion=accion,
        actor=actor,
        usuario_afectado=usuario_afectado,
        usuario_afectado_texto=(
            usuario_texto if usuario_texto is not None
            else (usuario_afectado.get_username() if usuario_afectado else '')
        )[:150],
        objeto=objeto[:200],
        campo=campo,
        valor_anterior='' if valor_anterior is None else str(valor_anterior),
        valor_nuevo='' if valor_nuevo is None else str(valor_nuevo),
        detalle=detalle[:255],
        ip=obtener_ip(request),
    )


def registrar_cambios(accion, cambios, **kwargs):
    """
    Registra una fila por cada campo modificado.
    `cambios` es una lista de tuplas (etiqueta_campo, valor_anterior, valor_nuevo).
    Devuelve cuántos cambios se registraron.
    """
    for campo, anterior, nuevo in cambios:
        registrar(accion, campo=campo, valor_anterior=anterior, valor_nuevo=nuevo, **kwargs)
    return len(cambios)


def _texto(valor):
    if valor is None:
        return ''
    if isinstance(valor, bool):
        return 'Sí' if valor else 'No'
    return str(valor)


def detectar_cambios(form, valores_iniciales):
    """
    Compara los valores originales con los del formulario ya validado.
    `valores_iniciales` es un dict {nombre_campo: valor_original} que se debe
    tomar ANTES de llamar a form.is_valid() (un ModelForm modifica la
    instancia al validar).
    Devuelve lista de (label, anterior, nuevo) solo con lo que cambió.
    """
    cambios = []
    for nombre, anterior in valores_iniciales.items():
        if nombre not in form.cleaned_data:
            continue
        nuevo = form.cleaned_data[nombre]
        if _texto(anterior) != _texto(nuevo):
            etiqueta = str(form.fields[nombre].label or nombre)
            cambios.append((etiqueta, _texto(anterior), _texto(nuevo)))
    return cambios
