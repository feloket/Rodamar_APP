"""
Validación y normalización de datos chilenos / automotrices.

Cada dato tiene dos funciones:
  - normalizar_x(valor): deja el valor en un formato único (mayúsculas,
    sin espacios, puntos y guion en su lugar). Así "76123456k" y
    "76.123.456-K" se guardan igual y la restricción unique funciona.
  - validar_x(valor): lanza ValidationError si el valor no es válido.
    Se usan como `validators=[...]` en los modelos, así validan tanto
    los formularios del sitio como /admin/.
"""
import re

from django.core.exceptions import ValidationError

# ---------------------------------------------------------------------------
# VIN / Chasis (norma ISO 3779): 17 caracteres, sin I, O ni Q
# (se excluyen para no confundirlas con 1 y 0).
# No se valida el dígito verificador (posición 9) porque solo es
# obligatorio en vehículos fabricados para Norteamérica.
# ---------------------------------------------------------------------------
_VIN = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')


def normalizar_vin(valor):
    return re.sub(r'[\s\-]', '', (valor or '')).upper()


def validar_vin(valor):
    vin = normalizar_vin(valor)
    if len(vin) != 17:
        raise ValidationError(f'El VIN debe tener 17 caracteres (tiene {len(vin)}).', code='vin_largo')
    if re.search(r'[IOQ]', vin):
        raise ValidationError('El VIN no puede contener las letras I, O ni Q.', code='vin_letras')
    if not _VIN.match(vin):
        raise ValidationError('El VIN solo puede tener letras y números.', code='vin_caracteres')


# ---------------------------------------------------------------------------
# RUT chileno con dígito verificador (módulo 11)
# ---------------------------------------------------------------------------
def calcular_dv(cuerpo):
    """Dígito verificador de un RUT (cuerpo solo con números)."""
    suma, factor = 0, 2
    for digito in reversed(str(cuerpo)):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    return {11: '0', 10: 'K'}.get(resto, str(resto))


def _separar_rut(valor):
    limpio = re.sub(r'[\s.\-]', '', (valor or '')).upper()
    return limpio[:-1], limpio[-1:]


def normalizar_rut(valor):
    """'76123456k' -> '76.123.456-K'. Si no parece RUT, lo devuelve tal cual (validar_rut avisará)."""
    cuerpo, dv = _separar_rut(valor)
    if not cuerpo.isdigit() or not dv:
        return (valor or '').strip().upper()
    cuerpo = str(int(cuerpo))  # quita ceros a la izquierda
    con_puntos = f'{int(cuerpo):,}'.replace(',', '.')
    return f'{con_puntos}-{dv}'


def validar_rut(valor):
    cuerpo, dv = _separar_rut(valor)
    if not cuerpo.isdigit() or not re.fullmatch(r'[0-9K]', dv or ''):
        raise ValidationError('Formato de RUT inválido. Ejemplo: 76.123.456-0', code='rut_formato')
    if not (1_000_000 <= int(cuerpo) <= 99_999_999):
        raise ValidationError('El RUT tiene un largo inválido.', code='rut_largo')
    if calcular_dv(cuerpo) != dv:
        raise ValidationError('El dígito verificador del RUT no es correcto.', code='rut_dv')


# ---------------------------------------------------------------------------
# Patente chilena (vehículos): formato antiguo AB·1234 o nuevo BCDF·12.
# En el formato nuevo solo se usan consonantes (sin vocales ni M, N, Ñ, Q).
# ---------------------------------------------------------------------------
_PATENTE_ANTIGUA = re.compile(r'^[A-Z]{2}\d{4}$')
_PATENTE_NUEVA = re.compile(r'^[BCDFGHJKLPRSTVWXYZ]{4}\d{2}$')


def _patente_limpia(valor):
    return re.sub(r'[\s.\-·]', '', (valor or '')).upper()


def normalizar_patente(valor):
    """'kxtr21' -> 'KXTR-21', 'ab1234' -> 'AB-1234'."""
    p = _patente_limpia(valor)
    if _PATENTE_NUEVA.match(p):
        return f'{p[:4]}-{p[4:]}'
    if _PATENTE_ANTIGUA.match(p):
        return f'{p[:2]}-{p[2:]}'
    return p


def validar_patente(valor):
    p = _patente_limpia(valor)
    if not (_PATENTE_NUEVA.match(p) or _PATENTE_ANTIGUA.match(p)):
        raise ValidationError(
            'Patente inválida. Formatos aceptados: BCDF-12 (actual) o AB-1234 (antiguo).',
            code='patente_formato',
        )
