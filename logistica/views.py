from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Vehiculo, Buque, Cliente, CamionCiguena
from .forms import VehiculoForm, BuqueForm, ClienteForm, CamionCiguenaForm

# Vista pública: Rastreo por número de chasis
def rastreo_vehiculo(request):
    query = request.GET.get('chasis', '').strip()
    vehiculo = None
    mensaje_error = None

    if query:
        try:
            vehiculo = Vehiculo.objects.get(chasis__iexact=query)
        except Vehiculo.DoesNotExist:
            mensaje_error = f"No se encontró ningún vehículo con el chasis '{query}'."

    return render(request, 'logistica/rastreo.html', {
        'vehiculo': vehiculo,
        'query': query,
        'mensaje_error': mensaje_error
    })

# Vista privada: Panel operativo para el operador
@login_required
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

# Guardar nuevo buque desde el modal
@login_required
def registrar_buque(request):
    if request.method == 'POST':
        form = BuqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Buque registrado exitosamente.")
        else:
            messages.error(request, "Error al registrar buque.")
    return redirect('dashboard')

# Guardar nuevo cliente desde el modal
@login_required
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado exitosamente.")
        else:
            messages.error(request, "Error al registrar cliente.")
    return redirect('dashboard')

# Guardar nuevo camión cigüeña desde el modal
@login_required
def registrar_camion(request):
    if request.method == 'POST':
        form = CamionCiguenaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Camión cigüeña registrado exitosamente.")
        else:
            messages.error(request, "Error al registrar camión.")
    return redirect('dashboard')

# Guardar nuevo vehículo desde el modal
@login_required
def registrar_vehiculo(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehículo ingresado al manifiesto.")
        else:
            messages.error(request, "Error al registrar vehículo. Verifique los campos.")
    return redirect('dashboard')

# Actualización rápida de estado y patio desde la tabla
@login_required
def actualizar_estado_vehiculo(request, pk):
    if request.method == 'POST':
        vehiculo = get_object_or_404(Vehiculo, pk=pk)
        nuevo_estado = request.POST.get('nuevo_estado')
        nueva_ubicacion = request.POST.get('ubicacion_patio')
        
        if nuevo_estado:
            vehiculo.estado = nuevo_estado
        if nueva_ubicacion is not None:
            vehiculo.ubicacion_patio = nueva_ubicacion
            
        vehiculo.save()
        messages.success(request, f"Actualizado chasis {vehiculo.chasis}.")
    return redirect('dashboard')