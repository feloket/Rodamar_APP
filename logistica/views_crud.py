"""
CRUD completo (listar, crear, editar, eliminar) de buques, camiones
cigüeña, vehículos y empresas cliente.

Permisos (mismos criterios que las cuentas de usuario):
  - Listar / crear / editar: ADMIN y EMPLEADO.
  - Eliminar: solo ADMIN.
Todo cambio queda en la auditoría; los cambios de estado/patio de un
vehículo además quedan en su HistorialEstado.
"""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render

from usuarios import auditoria, roles
from usuarios.models import RegistroAuditoria

from .forms import BuqueForm, CamionCiguenaForm, ClienteForm, VehiculoForm
from .models import Buque, CamionCiguena, Cliente, Vehiculo

solo_personal = roles.rol_requerido(roles.ADMIN, roles.EMPLEADO)
solo_admin = roles.rol_requerido(roles.ADMIN)

POR_PAGINA = 20


# ---------------------------------------------------------------------------
# Helpers genéricos (los usan los 4 modelos)
# ---------------------------------------------------------------------------
def _paginar(request, queryset):
    return Paginator(queryset, POR_PAGINA).get_page(request.GET.get('page'))


def _valores(instancia, form_class):
    """Valores actuales de los campos del formulario (antes de editar)."""
    return {campo: getattr(instancia, campo) for campo in form_class._meta.fields}


def vista_formulario(request, *, form_class, titulo, volver, instancia=None,
                     describir=str, despues_de_guardar=None):
    """
    Muestra y procesa un formulario de creación (instancia=None) o edición.
    Audita la creación o cada campo modificado.
    """
    creando = instancia is None
    if request.method == 'POST':
        form = form_class(request.POST, instance=instancia)
        iniciales = {} if creando else _valores(instancia, form_class)
        if form.is_valid():
            cambios = [] if creando else auditoria.detectar_cambios(form, iniciales)
            objeto = form.save()
            if despues_de_guardar:
                despues_de_guardar(objeto, iniciales)
            if creando:
                auditoria.registrar(RegistroAuditoria.CREACION_REGISTRO, request=request, objeto=describir(objeto))
                messages.success(request, f"{titulo} creado: {objeto}.")
            elif cambios:
                auditoria.registrar_cambios(RegistroAuditoria.EDICION_REGISTRO, cambios,
                                            request=request, objeto=describir(objeto))
                messages.success(request, f"{titulo} actualizado ({len(cambios)} cambio(s)).")
            else:
                messages.info(request, "No hubo cambios.")
            return redirect(volver)
        messages.error(request, "Revisa los datos marcados en rojo.")
    else:
        form = form_class(instance=instancia)

    return render(request, 'logistica/registro_form.html', {
        'form': form,
        'titulo': titulo,
        'creando': creando,
        'objeto': instancia,
        'volver': volver,
    })


def vista_eliminar(request, *, objeto, titulo, volver, describir=str, advertencia=''):
    """GET: confirmación. POST: elimina (con PROTECT avisa qué lo impide)."""
    if request.method == 'POST':
        descripcion = describir(objeto)
        try:
            objeto.delete()
        except ProtectedError as error:
            cantidad = len(error.protected_objects)
            messages.error(request, f"No se puede eliminar {descripcion}: tiene {cantidad} vehículo(s) asociado(s). "
                                    f"Reasígnalos o elimínalos primero.")
            return redirect(volver)
        auditoria.registrar(RegistroAuditoria.ELIMINACION_REGISTRO, request=request, objeto=descripcion)
        messages.success(request, f"{titulo} eliminado: {descripcion}.")
        return redirect(volver)

    return render(request, 'logistica/registro_eliminar.html', {
        'objeto': objeto,
        'titulo': titulo,
        'volver': volver,
        'advertencia': advertencia,
    })


# ---------------------------------------------------------------------------
# Buques
# ---------------------------------------------------------------------------
def _describir_buque(b):
    return f'Buque #{b.pk} {b.nombre} ({b.numero_viaje})'


@solo_personal
def buques_lista(request):
    q = request.GET.get('q', '').strip()
    buques = Buque.objects.annotate(
        total=Count('vehiculos'),
        pendientes=Count('vehiculos', filter=~Q(vehiculos__estado='ENTREGADO')),
    ).order_by('-fecha_atraque', 'nombre')
    if q:
        buques = buques.filter(Q(nombre__icontains=q) | Q(numero_viaje__icontains=q))
    return render(request, 'logistica/buques.html', {'pagina': _paginar(request, buques), 'q': q})


@solo_personal
def buque_crear(request):
    return vista_formulario(request, form_class=BuqueForm, titulo='Buque', volver='buques_lista',
                            describir=_describir_buque)


@solo_personal
def buque_editar(request, pk):
    return vista_formulario(request, form_class=BuqueForm, titulo='Buque', volver='buques_lista',
                            instancia=get_object_or_404(Buque, pk=pk), describir=_describir_buque)


@solo_admin
def buque_eliminar(request, pk):
    buque = get_object_or_404(Buque, pk=pk)
    return vista_eliminar(request, objeto=buque, titulo='Buque', volver='buques_lista',
                          describir=_describir_buque,
                          advertencia='Un buque con vehículos en su manifiesto no se puede eliminar.')


# ---------------------------------------------------------------------------
# Camiones cigüeña
# ---------------------------------------------------------------------------
def _describir_camion(c):
    return f'Camión #{c.pk} {c.patente} ({c.empresa_transporte})'


@solo_personal
def camiones_lista(request):
    q = request.GET.get('q', '').strip()
    camiones = CamionCiguena.objects.annotate(
        cargados=Count('vehiculos_cargados', filter=~Q(vehiculos_cargados__estado='ENTREGADO')),
        entregados=Count('vehiculos_cargados', filter=Q(vehiculos_cargados__estado='ENTREGADO')),
    ).order_by('patente')
    if q:
        camiones = camiones.filter(
            Q(patente__icontains=q) | Q(empresa_transporte__icontains=q) | Q(nombre_chofer__icontains=q))
    return render(request, 'logistica/camiones.html', {'pagina': _paginar(request, camiones), 'q': q})


@solo_personal
def camion_crear(request):
    return vista_formulario(request, form_class=CamionCiguenaForm, titulo='Camión', volver='camiones_lista',
                            describir=_describir_camion)


@solo_personal
def camion_editar(request, pk):
    return vista_formulario(request, form_class=CamionCiguenaForm, titulo='Camión', volver='camiones_lista',
                            instancia=get_object_or_404(CamionCiguena, pk=pk), describir=_describir_camion)


@solo_admin
def camion_eliminar(request, pk):
    camion = get_object_or_404(CamionCiguena, pk=pk)
    return vista_eliminar(request, objeto=camion, titulo='Camión', volver='camiones_lista',
                          describir=_describir_camion,
                          advertencia='Los vehículos asignados a este camión quedarán sin cigüeña asignada.')


# ---------------------------------------------------------------------------
# Vehículos
# ---------------------------------------------------------------------------
def _describir_vehiculo(v):
    return f'Vehículo #{v.pk} {v.chasis} ({v.marca} {v.modelo})'


def _historial_si_cambio(vehiculo, iniciales, usuario):
    """Si cambió el estado o el patio, lo registra en el historial del vehículo."""
    estado_ant = iniciales.get('estado', '')
    patio_ant = iniciales.get('ubicacion_patio') or ''
    if not iniciales:  # creación
        vehiculo.registrar_cambio(usuario, nota='Ingreso al manifiesto')
    elif estado_ant != vehiculo.estado or patio_ant != (vehiculo.ubicacion_patio or ''):
        vehiculo.registrar_cambio(usuario, estado_anterior=estado_ant, ubicacion_anterior=patio_ant,
                                  nota='Edición del vehículo')


@solo_personal
def vehiculos_lista(request):
    q = request.GET.get('q', '').strip()
    filtros = {
        'estado': request.GET.get('estado', ''),
        'buque': request.GET.get('buque', ''),
        'empresa': request.GET.get('empresa', ''),
    }
    vehiculos = Vehiculo.objects.select_related('buque', 'cliente', 'camion_ciguena').order_by('-fecha_registro')
    if q:
        vehiculos = vehiculos.filter(Q(chasis__icontains=q) | Q(marca__icontains=q) | Q(modelo__icontains=q))
    if filtros['estado']:
        vehiculos = vehiculos.filter(estado=filtros['estado'])
    if filtros['buque'].isdigit():
        vehiculos = vehiculos.filter(buque_id=filtros['buque'])
    if filtros['empresa'].isdigit():
        vehiculos = vehiculos.filter(cliente_id=filtros['empresa'])

    return render(request, 'logistica/vehiculos.html', {
        'pagina': _paginar(request, vehiculos),
        'q': q,
        'filtros': filtros,
        'estados': Vehiculo.ESTADOS,
        'buques': Buque.objects.order_by('-fecha_atraque'),
        'empresas': Cliente.objects.order_by('nombre_completo'),
        'total': vehiculos.count(),
    })


@solo_personal
def vehiculo_crear(request):
    return vista_formulario(request, form_class=VehiculoForm, titulo='Vehículo', volver='vehiculos_lista',
                            describir=_describir_vehiculo,
                            despues_de_guardar=lambda v, ini: _historial_si_cambio(v, ini, request.user))


@solo_personal
def vehiculo_editar(request, pk):
    return vista_formulario(request, form_class=VehiculoForm, titulo='Vehículo', volver='vehiculos_lista',
                            instancia=get_object_or_404(Vehiculo, pk=pk), describir=_describir_vehiculo,
                            despues_de_guardar=lambda v, ini: _historial_si_cambio(v, ini, request.user))


@solo_admin
def vehiculo_eliminar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    return vista_eliminar(request, objeto=vehiculo, titulo='Vehículo', volver='vehiculos_lista',
                          describir=_describir_vehiculo,
                          advertencia='También se borrará su historial de estados (la eliminación queda en la auditoría).')


# ---------------------------------------------------------------------------
# Empresas cliente (listar y editar ya existen en views.py)
# ---------------------------------------------------------------------------
def _describir_empresa(e):
    return f'Empresa #{e.pk} {e.nombre_completo} ({e.rut_o_id})'


@solo_personal
def empresa_crear(request):
    return vista_formulario(request, form_class=ClienteForm, titulo='Empresa', volver='lista_empresas',
                            describir=_describir_empresa)


@solo_admin
def empresa_eliminar(request, pk):
    empresa = get_object_or_404(Cliente, pk=pk)
    return vista_eliminar(request, objeto=empresa, titulo='Empresa', volver='lista_empresas',
                          describir=_describir_empresa,
                          advertencia='Una empresa con vehículos no se puede eliminar. '
                                      'Las cuentas de cliente vinculadas quedarán sin empresa.')
