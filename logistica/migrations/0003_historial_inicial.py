"""Crea una entrada inicial de historial para los vehículos que ya existían."""
from django.db import migrations


def avanzar(apps, schema_editor):
    Vehiculo = apps.get_model('logistica', 'Vehiculo')
    HistorialEstado = apps.get_model('logistica', 'HistorialEstado')
    for v in Vehiculo.objects.all():
        if not HistorialEstado.objects.filter(vehiculo=v).exists():
            h = HistorialEstado.objects.create(
                vehiculo=v, estado_nuevo=v.estado, ubicacion_nueva=v.ubicacion_patio or '',
                usuario_texto='Sistema', nota='Estado al activar el historial',
            )
            # Se fecha con el registro original del vehículo
            HistorialEstado.objects.filter(pk=h.pk).update(fecha=v.fecha_registro)


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0002_proteger_y_historial'),
    ]

    operations = [
        migrations.RunPython(avanzar, migrations.RunPython.noop),
    ]
