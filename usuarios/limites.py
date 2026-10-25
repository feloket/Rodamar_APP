"""
Límite simple de peticiones usando la caché de Django.
Sirve para frenar abusos (probar chasis uno tras otro, pedir muchos correos
de recuperación, etc.) sin instalar librerías extra.

Nota: la caché por defecto (LocMemCache) vive en la memoria de cada proceso;
para un proyecto local es suficiente. En producción se usaría Redis/Memcached.
"""
from django.core.cache import cache


def excede_limite(clave, maximo, segundos):
    """
    Suma 1 al contador de `clave` y devuelve True si ya pasó `maximo`
    dentro de la ventana de `segundos`.
    """
    clave = f'limite:{clave}'
    # add() solo crea la clave si no existe (inicia la ventana de tiempo)
    if cache.add(clave, 1, timeout=segundos):
        return False
    try:
        intentos = cache.incr(clave)
    except ValueError:  # la clave expiró entre add() e incr()
        cache.set(clave, 1, timeout=segundos)
        return False
    return intentos > maximo
