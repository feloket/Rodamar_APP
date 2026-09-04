from django.contrib import admin
from .models import Buque, Cliente, CamionCiguena, Vehiculo

# Registramos las 4 tablas en el panel de administración
admin.site.register(Buque)
admin.site.register(Cliente)
admin.site.register(CamionCiguena)
admin.site.register(Vehiculo)