"""
Migración de datos:
  1. Crea los grupos "Empleados" y "Clientes".
  2. Crea el Perfil de los usuarios que ya existían.
  3. Las cuentas del grupo antiguo "Operadores" (registro público de la
     versión anterior) pasan a "Clientes" por mínimo privilegio. Si alguna
     era de un empleado real, un admin la cambia desde Gestión de usuarios.
"""
from django.conf import settings
from django.db import migrations


def avanzar(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Perfil = apps.get_model('usuarios', 'Perfil')

    Group.objects.get_or_create(name='Empleados')
    clientes, _ = Group.objects.get_or_create(name='Clientes')

    for usuario in User.objects.all():
        Perfil.objects.get_or_create(usuario=usuario)

    legado = Group.objects.filter(name='Operadores').first()
    if legado:
        for usuario in legado.user_set.filter(is_superuser=False):
            usuario.groups.add(clientes)
            usuario.groups.remove(legado)


def retroceder(apps, schema_editor):
    # Los grupos y perfiles se dejan; revertir no borra datos de usuarios.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(avanzar, retroceder),
    ]
