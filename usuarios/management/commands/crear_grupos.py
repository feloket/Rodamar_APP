from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from usuarios.roles import GRUPO_CLIENTES, GRUPO_EMPLEADOS


class Command(BaseCommand):
    help = "Crea los grupos de roles ('Empleados' y 'Clientes') si no existen."

    def handle(self, *args, **options):
        # Normalmente no hace falta: la migración usuarios.0002 ya los crea.
        for nombre in (GRUPO_EMPLEADOS, GRUPO_CLIENTES):
            _, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f"Grupo '{nombre}' creado."))
            else:
                self.stdout.write(f"El grupo '{nombre}' ya existía.")
