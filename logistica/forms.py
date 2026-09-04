from django import forms
from .models import Vehiculo, Buque, Cliente, CamionCiguena

# Formulario para registrar un Buque
class BuqueForm(forms.ModelForm):
    class Meta:
        model = Buque
        fields = ['nombre', 'numero_viaje', 'fecha_atraque']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Glovis Stella'}),
            'numero_viaje': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-2026-01'}),
            'fecha_atraque': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formulario para registrar un Cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_completo', 'rut_o_id', 'telefono', 'email']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Automotriz del Norte'}),
            'rut_o_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.123.456-K'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.cl'}),
        }

# Formulario para registrar una Cigüeña / Camión
class CamionCiguenaForm(forms.ModelForm):
    class Meta:
        model = CamionCiguena
        fields = ['patente', 'empresa_transporte', 'nombre_chofer', 'rut_chofer']
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABCD-12'}),
            'empresa_transporte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Transportes del Pacífico'}),
            'nombre_chofer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'rut_chofer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15.432.198-7'}),
        }

# Formulario para registrar un Vehículo
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['chasis', 'marca', 'modelo', 'color', 'buque', 'cliente', 'camion_ciguena', 'estado', 'ubicacion_patio']
        widgets = {
            'chasis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VIN / Chasis'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Hilux'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco'}),
            'buque': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'camion_ciguena': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_patio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bloque A - Fila 3'}),
        }