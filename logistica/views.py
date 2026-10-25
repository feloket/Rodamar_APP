from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from usuarios import auditoria, roles
from usuarios.limites import excede_limite
from usuarios.models import Perfil, RegistroAuditoria
from .models import Vehiculo, Buque, Cliente, CamionCiguena
from .forms import VehiculoForm, BuqueForm, ClienteForm, CamionCiguenaForm
from . import views_crud
from .validadores import normalizar_vin

# Las vistas operativas (panel, registrar buques/vehículos/clientes/camiones,
# actualizar estados) son SOLO para personal: ADMIN y EMPLEADO.
# Un CLIENTE autenticado recibe 403 si intenta entrar (aunque escriba la URL).
solo_personal = roles.rol_requerido(roles.ADMIN, roles.EMPLEADO)

# Límite de consultas públicas de rastreo por IP (evita probar chasis en masa)
RASTREO_MAX_CONSULTAS = 20
RASTREO_VENTANA_SEGUNDOS = 10 * 60


def _puede_ver_detalle(user, vehiculo):
    """Personal ve todo; un cliente solo los vehículos de SU empresa."""
    if roles.es_personal(user):
        return True
    if user.is_authenticated:
        perfil = Perfil.objects.filter(usuario=user).first()
        return bool(perfil and perfil.empresa_id and perfil.empresa_id == vehiculo.cliente_id)
    return False


# Vista pública: Rastreo por número de chasis.
# - Visitantes y clientes ajenos: solo estado, marca/modelo y patio.
# - Dueño (cliente de esa empresa) y personal: además consignatario, buque,
#   cigüeña e historial de estados.
def rastreo_vehiculo(request):
    query = normalizar_vin(request.GET.get('chasis', ''))[:50]
    vehiculo = None
    mensaje_error = None
    detalle = False
    historial = []

    if query:
        # El personal no tiene límite; el resto sí (por IP)
        ip = auditoria.obtener_ip(request) or 'sin-ip'
        if not roles.es_personal(request.user) and excede_limite(
                f'rastreo:{ip}', RASTREO_MAX_CONSULTAS, RASTREO_VENTANA_SEGUNDOS):
            mensaje_error = "Hiciste demasiadas consultas seguidas. Espera unos minutos e inténtalo de nuevo."
        else:
            vehiculo = Vehiculo.objects.select_related('buque', 'cliente', 'camion_ciguena').filter(
                chasis__iexact=query).first()
            if vehiculo is None:
                mensaje_error = f"No se encontró ningún vehículo con el chasis '{query}'."
            else:
                detalle = _puede_ver_detalle(request.user, vehiculo)
                if detalle:
                    historial = vehiculo.historial.all()

    return render(request, 'logistica/rastreo.html', {
        'vehiculo': vehiculo,
        'query': query,
        'mensaje_error': mensaje_error,
        'detalle': detalle,
        'historial': historial,
    })

# Vista privada: Panel operativo para el operador
@solo_personal
def dashboard_operaciones(request):
    q = request.GET.get('q', '').strip()
    filtro_estado = request.GET.get('estado', '')
    
    vehiculos = Vehiculo.objects.all().select_related('buque', 'cliente', 'camion_ciguena')
    if q:
        vehiculos = vehiculos.filter(chasis__icontains=q)
    if filtro_estado:
        vehiculos = vehiculos.filter(estado=filtro_estado)

    # Contadores de métricas
    total = Vehiculo.objects.count()
    encontrados = Vehiculo.objects.filter(estado='ENCONTRADO').count()
    en_proceso = Vehiculo.objects.filter(estado='EN_PROCESO').count()
    en_camino = Vehiculo.objects.filter(estado='EN_CAMINO').count()
    entregados = Vehiculo.objects.filter(estado='ENTREGADO').count()

    return render(request, 'logistica/dashboard.html', {
        'vehiculos': vehiculos,
        'form': VehiculoForm(),
        'form_buque': BuqueForm(),
        'form_cliente': ClienteForm(),
        'form_camion': CamionCiguenaForm(),
        'total': total,
        'encontrados': encontrados,
        'en_proceso': en_proceso,
        'en_camino': en_camino,
        'entregados': entregados,
        'q': q,
        'filtro_estado': filtro_estado,
        'estados': Vehiculo.ESTADOS,
    })

# Guardar desde los modales del panel.
# Si el formulario tiene errores, en vez de volver al panel y perder lo
# escrito, se muestra la página del formulario con los errores marcados.
# (La lógica común está en views_crud.vista_formulario.)
@solo_personal
def registrar_buque(request):
    return views_crud.vista_formulario(request, form_class=BuqueForm, titulo='Buque', volver='dashboard',
                                       describir=views_crud._describir_buque)


@solo_personal
def registrar_cliente(request):
    volver = 'lista_empresas' if request.POST.get('volver') == 'empresas' else 'dashboard'
    return views_crud.vista_formulario(request, form_class=ClienteForm, titulo='Empresa', volver=volver,
                                       describir=views_crud._describir_empresa)


@solo_personal
def registrar_camion(request):
    return views_crud.vista_formulario(request, form_class=CamionCiguenaForm, titulo='Camión', volver='dashboard',
                                       describir=views_crud._describir_camion)


@solo_personal
def registrar_vehiculo(request):
    return views_crud.vista_formulario(
        request, form_class=VehiculoForm, titulo='Vehículo', volver='dashboard',
        describir=views_crud._describir_vehiculo,
        despues_de_guardar=lambda v, ini: views_crud._historial_si_cambio(v, ini, request.user),
    )

# Actualización rápida de estado y patio desde la tabla
@solo_personal
def actualizar_estado_vehiculo(request, pk):
    if request.method == 'POST':
        vehiculo = get_object_or_404(Vehiculo, pk=pk)
        nuevo_estado = request.POST.get('nuevo_estado')
        nueva_ubicacion = request.POST.get('ubicacion_patio')
        
        estados_validos = dict(Vehiculo.ESTADOS)
        if nuevo_estado and nuevo_estado not in estados_validos:
            messages.error(request, "Estado no válido.")
            return redirect('dashboard')
        estado_anterior = vehiculo.estado
        ubicacion_anterior = vehiculo.ubicacion_patio or ''
        if nuevo_estado:
            vehiculo.estado = nuevo_estado
        if nueva_ubicacion is not None:
            vehiculo.ubicacion_patio = nueva_ubicacion.strip()[:60]

        if vehiculo.estado == estado_anterior and (vehiculo.ubicacion_patio or '') == ubicacion_anterior:
            messages.info(request, f"Chasis {vehiculo.chasis}: no hubo cambios.")
            return redirect('dashboard')

        vehiculo.save()
        # Trazabilidad: quién cambió qué y cuándo
        vehiculo.registrar_cambio(request.user, estado_anterior=estado_anterior, ubicacion_anterior=ubicacion_anterior)
        messages.success(request, f"Actualizado chasis {vehiculo.chasis}.")
    return redirect('dashboard')


# Vista del CLIENTE: solo los vehículos de la empresa vinculada a su cuenta.
@login_required
def mis_vehiculos(request):
    if roles.es_personal(request.user):
        return redirect('dashboard')
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    empresa = perfil.empresa
    vehiculos = Vehiculo.objects.none()
    if empresa:
        vehiculos = empresa.vehiculos.select_related('buque', 'camion_ciguena').order_by('-fecha_registro')
    return render(request, 'logistica/mis_vehiculos.html', {
        'empresa': empresa,
        'vehiculos': vehiculos,
    })


# Listado de empresas cliente (personal). Muestra cuántas cuentas y vehículos tiene cada una.
@solo_personal
def lista_empresas(request):
    q = request.GET.get('q', '').strip()
    empresas = Cliente.objects.annotate(
        total_vehiculos=Count('vehiculos', distinct=True),
        total_cuentas=Count('cuentas', distinct=True),
    ).order_by('nombre_completo')
    if q:
        empresas = empresas.filter(Q(nombre_completo__icontains=q) | Q(rut_o_id__icontains=q))
    return render(request, 'logistica/empresas.html', {
        'empresas': empresas,
        'q': q,
        'form_cliente': ClienteForm(),
    })


# Edición de una empresa cliente (personal). Cada cambio queda auditado.
@solo_personal
def editar_empresa(request, pk):
    empresa = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        campos = ['nombre_completo', 'rut_o_id', 'telefono', 'email']
        iniciales = {c: getattr(empresa, c) for c in campos}
        form = ClienteForm(request.POST, instance=empresa)
        if form.is_valid():
            cambios = auditoria.detectar_cambios(form, iniciales)
            form.save()
            auditoria.registrar_cambios(
                RegistroAuditoria.EDICION_EMPRESA, cambios, request=request,
                objeto=f'Empresa #{empresa.pk} ({empresa.rut_o_id})',
            )
            messages.success(request, f"Empresa '{empresa.nombre_completo}' actualizada.")
            return redirect('lista_empresas')
        messages.error(request, "Revisa los datos ingresados.")
    else:
        form = ClienteForm(instance=empresa)
    return render(request, 'logistica/empresa_form.html', {
        'form': form,
        'empresa': empresa,
        'cuentas': empresa.cuentas.select_related('usuario'),
    })
