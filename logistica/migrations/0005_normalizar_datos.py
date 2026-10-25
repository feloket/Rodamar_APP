"""
Normaliza los datos que ya existían (VIN en mayúsculas, RUT con puntos y
guion, patente con guion). Si al normalizar dos registros quedarían
iguales, NO se toca ninguno de los dos y se avisa en la consola para que
se revisen a mano (no se pierden datos).
Los valores que no cumplan el formato nuevo se dejan como están: el
sistema pedirá corregirlos la próxima vez que se editen.
"""
from django.db import migrations

from logistica.validadores import normalizar_patente, normalizar_rut, normalizar_vin


def _normalizar(Modelo, campo, funcion):
    existentes = list(Modelo.objects.exclude(**{f'{campo}__isnull': True}).values_list('pk', campo))
    nuevos = {}
    for pk, valor in existentes:
        nuevos.setdefault(funcion(valor), []).append((pk, valor))
    for normalizado, filas in nuevos.items():
        if len(filas) > 1:
            print(f"\n  [aviso] {Modelo.__name__}.{campo}: {[v for _, v in filas]} quedarían iguales "
                  f"('{normalizado}'). Revísalos a mano.")
            continue
        pk, valor = filas[0]
        if valor != normalizado:
            Modelo.objects.filter(pk=pk).update(**{campo: normalizado})


def avanzar(apps, schema_editor):
    _normalizar(apps.get_model('logistica', 'Vehiculo'), 'chasis', normalizar_vin)
    _normalizar(apps.get_model('logistica', 'Cliente'), 'rut_o_id', normalizar_rut)
    _normalizar(apps.get_model('logistica', 'CamionCiguena'), 'patente', normalizar_patente)
    Camion = apps.get_model('logistica', 'CamionCiguena')
    for c in Camion.objects.exclude(rut_chofer__isnull=True).exclude(rut_chofer=''):
        Camion.objects.filter(pk=c.pk).update(rut_chofer=normalizar_rut(c.rut_chofer))


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0004_validaciones'),
    ]

    operations = [
        migrations.RunPython(avanzar, migrations.RunPython.noop),
    ]
