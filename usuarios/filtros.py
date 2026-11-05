"""
Filtros de fecha y orden que comparten los listados (auditoría, historial de
cuenta, panel de operaciones y rastreo).

No usa __month, __day ni __hour del ORM: con USE_TZ=True, esos filtros necesitan
las tablas de zona horaria de MySQL, que en Windows normalmente no vienen
instaladas, y sin ellas devuelven resultados vacíos sin avisar. El año se filtra
por rango en la base, y el resto se compara en Python con la hora de Chile.
"""
from datetime import datetime, time

from django.db.models import Max, Min
from django.utils import timezone

MESES = [
    (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'),
    (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
]
RECIENTES = 'recientes'
ANTIGUOS = 'antiguos'


def _entero(valor, minimo, maximo):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    return numero if minimo <= numero <= maximo else None


def _hora(valor):
    try:
        return time.fromisoformat(valor or '')
    except ValueError:
        return None


def _en_horario(momento, desde, hasta):
    """Incluye el minuto de `hasta`. Si desde > hasta, el rango cruza la medianoche (22:00 a 06:00)."""
    actual = momento.time().replace(second=0, microsecond=0)
    if desde and hasta:
        return desde <= actual <= hasta if desde <= hasta else actual >= desde or actual <= hasta
    if desde:
        return actual >= desde
    return actual <= hasta if hasta else True


def filtrar_por_fecha(queryset, campo, datos):
    """
    Aplica los parámetros anio, mes, dia, hora_desde y hora_hasta; todos son
    opcionales y combinables. Devuelve (queryset, contexto para el formulario).
    """
    limites = queryset.aggregate(primero=Min(campo), ultimo=Max(campo))
    anios = []
    if limites['primero']:
        anios = list(range(timezone.localtime(limites['ultimo']).year,
                           timezone.localtime(limites['primero']).year - 1, -1))

    anio = _entero(datos.get('anio'), 1900, 2100)
    mes = _entero(datos.get('mes'), 1, 12)
    dia = _entero(datos.get('dia'), 1, 31)
    desde = _hora(datos.get('hora_desde'))
    hasta = _hora(datos.get('hora_hasta'))

    if anio:
        queryset = queryset.filter(**{
            f'{campo}__gte': timezone.make_aware(datetime(anio, 1, 1)),
            f'{campo}__lt': timezone.make_aware(datetime(anio + 1, 1, 1)),
        })
    if mes or dia or desde or hasta:
        coinciden = []
        for pk, valor in queryset.order_by().values_list('pk', campo):
            momento = timezone.localtime(valor)
            if ((not mes or momento.month == mes) and (not dia or momento.day == dia)
                    and _en_horario(momento, desde, hasta)):
                coinciden.append(pk)
        queryset = queryset.filter(pk__in=coinciden)

    return queryset, {
        'anios': anios,
        'meses': MESES,
        'dias': range(1, 32),
        'anio': anio,
        'mes': mes,
        'dia': dia,
        'hora_desde': desde.strftime('%H:%M') if desde else '',
        'hora_hasta': hasta.strftime('%H:%M') if hasta else '',
    }


def leer_orden(datos):
    return ANTIGUOS if datos.get('orden') == ANTIGUOS else RECIENTES


def ordenar(queryset, campo, datos):
    """Más recientes primero, salvo que se pida orden=antiguos."""
    if leer_orden(datos) == ANTIGUOS:
        return queryset.order_by(campo, 'pk')
    return queryset.order_by(f'-{campo}', '-pk')
