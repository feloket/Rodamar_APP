"""
Reglas de negocio del flujo de un vehículo en el puerto.

    1. ENCONTRADO -> 2. EN_PROCESO -> 3. EN_CAMINO -> 4. ENTREGADO

  - Un vehículo nuevo entra en el primer estado.
  - Un empleado avanza de a un paso. Así el historial muestra cada etapa.
  - Solo un admin puede retroceder o saltar estados, para corregir errores
    (el cambio igual queda en el historial y en la auditoría).
  - En traslado o entregado exige un camión cigüeña asignado, para todos.

Las usan el formulario de vehículo y la actualización rápida del panel, que
así no pueden aplicar reglas distintas.
"""
from usuarios import roles

ORDEN_ESTADOS = ['ENCONTRADO', 'EN_PROCESO', 'EN_CAMINO', 'ENTREGADO']
ESTADOS_CON_CAMION = {'EN_CAMINO', 'ENTREGADO'}


def error_de_estado(estado_actual, estado_nuevo, camion, usuario=None):
    """
    Devuelve el mensaje de error si el cambio no está permitido, o None si lo está.
    `estado_actual` es None cuando el vehículo se está creando.
    """
    if estado_nuevo in ESTADOS_CON_CAMION and not camion:
        return 'Para pasar a traslado o entrega debes asignar un camión cigüeña.'

    if estado_actual == estado_nuevo or roles.es_admin(usuario):
        return None

    if estado_actual is None:
        if estado_nuevo != ORDEN_ESTADOS[0]:
            return 'Un vehículo nuevo debe ingresar como "Descarga / Encontrado".'
        return None

    if ORDEN_ESTADOS.index(estado_nuevo) != ORDEN_ESTADOS.index(estado_actual) + 1:
        return 'Solo puedes avanzar al estado siguiente. Para corregir un estado, pídeselo a un administrador.'
    return None
