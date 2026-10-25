from django import forms

from usuarios.forms import BootstrapErroresMixin  # marca en rojo los campos con error
from .models import Vehiculo, Buque, Cliente, CamionCiguena
from .validadores import normalizar_patente, normalizar_rut, normalizar_vin

# Formulario para registrar un Buque
class BuqueForm(BootstrapErroresMixin, forms.ModelForm):
    class Meta:
        model = Buque
        fields = ['nombre', 'numero_viaje', 'fecha_atraque']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Glovis Stella'}),
            'numero_viaje': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-2026-01'}),
            'fecha_atraque': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formulario para registrar un Cliente
class ClienteForm(BootstrapErroresMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_completo', 'rut_o_id', 'telefono', 'email']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Automotriz del Norte'}),
            'rut_o_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.123.456-0'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.cl'}),
        }

    def clean_rut_o_id(self):
        return normalizar_rut(self.cleaned_data['rut_o_id'])

# Formulario para registrar una Cigüeña / Camión
class CamionCiguenaForm(BootstrapErroresMixin, forms.ModelForm):
    class Meta:
        model = CamionCiguena
        fields = ['patente', 'empresa_transporte', 'nombre_chofer', 'rut_chofer']
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'Ej: BCDF-12'}),
            'empresa_transporte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Transportes del Pacífico'}),
            'nombre_chofer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'rut_chofer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15.432.198-5'}),
        }

    def clean_patente(self):
        return normalizar_patente(self.cleaned_data['patente'])

    def clean_rut_chofer(self):
        rut = self.cleaned_data.get('rut_chofer')
        return normalizar_rut(rut) if rut else None

# Formulario para registrar un Vehículo
class VehiculoForm(BootstrapErroresMixin, forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['chasis', 'marca', 'modelo', 'color', 'buque', 'cliente', 'camion_ciguena', 'estado', 'ubicacion_patio']
        widgets = {
            'chasis': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': '17 caracteres, ej: JTDKB20U093456781', 'maxlength': 20}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Hilux'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco'}),
            'buque': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'camion_ciguena': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_patio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bloque A - Fila 3'}),
        }

    def clean_chasis(self):
        return normalizar_vin(self.cleaned_data['chasis'])
