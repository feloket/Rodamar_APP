from django.conf import settings
from django.db import models

from .validadores import (
    normalizar_patente, normalizar_rut, normalizar_vin,
    validar_patente, validar_rut, validar_vin,
)

# Tabla 1: Buque que arriba al puerto
class Buque(models.Model):
    # Nombre de la nave (ej. Glovis Stella)
    nombre = models.CharField('Nombre de la nave', max_length=120)
    # Código o número de viaje que hace el barco
    numero_viaje = models.CharField('Número de viaje', max_length=60)
    # Fecha exacta en que atraca en el muelle
    fecha_atraque = models.DateField('Fecha de atraque')

    def __str__(self):
        return f"{self.nombre} (Viaje: {self.numero_viaje})"


# Tabla 2: Cliente o empresa dueña de los vehículos
class Cliente(models.Model):
    # Razón Social o Nombre del consignatario
    nombre_completo = models.CharField('Razón social', max_length=150)
    # RUT o Identificador único (no repetible)
    rut_o_id = models.CharField('RUT', max_length=20, unique=True, validators=[validar_rut])
    # Datos de contacto
    telefono = models.CharField('Teléfono', max_length=30, blank=True, null=True)
    email = models.EmailField('Correo', blank=True, null=True)

    def clean_fields(self, exclude=None):
        # Normaliza ANTES de validar, para que unique compare el formato único
        self.rut_o_id = normalizar_rut(self.rut_o_id)
        super().clean_fields(exclude)

    def save(self, *args, **kwargs):
        # Solo al crear: al editar ya se normalizó en clean_fields/formulario.
        # (Si se normalizara siempre, un dato antiguo duplicado haría fallar
        # cualquier guardado del registro con un error 500.)
        if self._state.adding:
            self.rut_o_id = normalizar_rut(self.rut_o_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} - {self.rut_o_id}"


# Tabla 3: Camión Cigueña / Transporte Terrestre
class CamionCiguena(models.Model):
    patente = models.CharField(max_length=20, unique=True, verbose_name="Patente Camión", validators=[validar_patente])
    empresa_transporte = models.CharField('Empresa de transporte', max_length=100)
    nombre_chofer = models.CharField('Nombre del chofer', max_length=120, blank=True, null=True)
    rut_chofer = models.CharField('RUT del chofer', max_length=20, blank=True, null=True, validators=[validar_rut])

    def clean_fields(self, exclude=None):
        self._normalizar()
        super().clean_fields(exclude)

    def save(self, *args, **kwargs):
        if self._state.adding:  # ver comentario en Cliente.save
            self._normalizar()
        super().save(*args, **kwargs)

    def _normalizar(self):
        self.patente = normalizar_patente(self.patente)
        self.rut_chofer = normalizar_rut(self.rut_chofer) if self.rut_chofer else None

    def __str__(self):
        return f"Cigueña: {self.patente} ({self.empresa_transporte})"


# Tabla 4: Vehículos que se descargan en el puerto
class Vehiculo(models.Model):
    ESTADOS = [
        ('ENCONTRADO', '1. Descarga / Encontrado'),
        ('EN_PROCESO', '2. Inspección / En Proceso'),
        ('EN_CAMINO', '3. En Traslado / Faena'),
        ('ENTREGADO', '4. Entregado / Despachado'),
    ]

    chasis = models.CharField(max_length=50, unique=True, verbose_name="VIN / Chasis", validators=[validar_vin])
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    color = models.CharField(max_length=40, blank=True, null=True)
    ubicacion_patio = models.CharField('Ubicación en patio', max_length=60, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ENCONTRADO')
    
    # Relaciones del vehículo.
    # PROTECT: no se puede borrar un buque o una empresa mientras tenga
    # vehículos asociados (antes CASCADE borraba el manifiesto completo).
    buque = models.ForeignKey(Buque, on_delete=models.PROTECT, related_name='vehiculos')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='vehiculos', verbose_name='Empresa cliente')
    camion_ciguena = models.ForeignKey(
        CamionCiguena, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='vehiculos_cargados',
        verbose_name='Camión cigüeña',
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def clean_fields(self, exclude=None):
        self.chasis = normalizar_vin(self.chasis)
        super().clean_fields(exclude)

    def save(self, *args, **kwargs):
        if self._state.adding:  # ver comentario en Cliente.save
            self.chasis = normalizar_vin(self.chasis)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chasis} - {self.marca} {self.modelo}"

    def registrar_cambio(self, usuario, estado_anterior='', ubicacion_anterior='', nota=''):
        """Guarda en el historial el estado/ubicación ACTUAL del vehículo."""
        return HistorialEstado.objects.create(
            vehiculo=self,
            estado_anterior=estado_anterior or '',
            estado_nuevo=self.estado,
            ubicacion_anterior=ubicacion_anterior or '',
            ubicacion_nueva=self.ubicacion_patio or '',
            usuario=usuario if getattr(usuario, 'is_authenticated', False) else None,
            usuario_texto=usuario.get_username() if getattr(usuario, 'is_authenticated', False) else 'Sistema',
            nota=nota,
        )


# Tabla 5: Historial de estados del vehículo (trazabilidad).
# Cada cambio de estado o de ubicación en patio queda registrado con
# quién lo hizo y cuándo. No se edita: solo se agregan filas.
class HistorialEstado(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20, choices=Vehiculo.ESTADOS, blank=True)
    estado_nuevo = models.CharField(max_length=20, choices=Vehiculo.ESTADOS)
    ubicacion_anterior = models.CharField(max_length=60, blank=True)
    ubicacion_nueva = models.CharField(max_length=60, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cambios_estado',
    )
    # Se guarda también como texto para no perder el dato si se elimina la cuenta
    usuario_texto = models.CharField(max_length=150, blank=True)
    nota = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'Historial de estado'
        verbose_name_plural = 'Historial de estados'

    def __str__(self):
        return f"{self.vehiculo.chasis}: {self.estado_anterior or '—'} → {self.estado_nuevo}"

