from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crea el grupo 'Operadores' (rol USUARIO) si no existe todavía."

    def handle(self, *args, **options):
        grupo, creado = Group.objects.get_or_create(name='Operadores')
        if creado:
            self.stdout.write(self.style.SUCCESS("Grupo 'Operadores' creado."))
        else:
            self.stdout.write("El grupo 'Operadores' ya existía, no se hizo nada.")
