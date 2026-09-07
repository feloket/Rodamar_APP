from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import RegistroForm

# Nombre del grupo que representa el rol USUARIO (operador autenticado
# normal, sin permisos de administrador). Se usa también en
# usuarios/management/commands/crear_grupos.py
GRUPO_USUARIO = 'Operadores'


def registro_view(request):
    """
    Registro público para el rol USUARIO.
    El usuario creado NUNCA recibe is_staff/is_superuser aquí: eso solo
    se otorga manualmente desde /admin/ o con createsuperuser, para que
    nadie pueda auto-otorgarse permisos de administrador.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()  # is_staff/is_superuser quedan en False por defecto

            grupo_operadores, _ = Group.objects.get_or_create(name=GRUPO_USUARIO)
            usuario.groups.add(grupo_operadores)

            login(request, usuario)
            messages.success(request, f"¡Bienvenido, {usuario.username}! Tu cuenta fue creada.")
            return redirect('dashboard')
        else:
            messages.error(request, "Revisa los datos ingresados.")
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})
