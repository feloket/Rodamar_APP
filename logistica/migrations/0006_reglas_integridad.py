# Migración: camión PROTECT, buque+viaje único y teléfono validado

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logistica", "0005_normalizar_datos"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="telefono",
            field=models.CharField(
                blank=True,
                max_length=30,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Ingresa un teléfono válido, por ejemplo +56 9 1234 5678.",
                        regex="^\\+?[0-9 ]{8,15}$",
                    )
                ],
                verbose_name="Teléfono",
            ),
        ),
        migrations.AlterField(
            model_name="vehiculo",
            name="camion_ciguena",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="vehiculos_cargados",
                to="logistica.camionciguena",
                verbose_name="Camión cigüeña",
            ),
        ),
        migrations.AddConstraint(
            model_name="buque",
            constraint=models.UniqueConstraint(
                fields=("nombre", "numero_viaje"),
                name="buque_viaje_unico",
                violation_error_message="Ya existe un buque con ese nombre y número de viaje.",
            ),
        ),
    ]
