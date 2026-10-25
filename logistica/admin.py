from django.contrib import admin
from .models import Buque, Cliente, CamionCiguena, HistorialEstado, Vehiculo

# Registramos las 4 tablas en el panel de administración
admin.site.register(Buque)
admin.site.register(CamionCiguena)


# Cliente con búsqueda (la usa el autocompletado de empresa en el Perfil)
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'rut_o_id', 'telefono', 'email')
    search_fields = ('nombre_completo', 'rut_o_id')



class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    can_delete = False
    readonly_fields = ('fecha', 'estado_anterior', 'estado_nuevo', 'ubicacion_anterior', 'ubicacion_nueva', 'usuario_texto', 'nota')
    exclude = ('usuario',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('chasis', 'marca', 'modelo', 'cliente', 'buque', 'estado', 'ubicacion_patio')
    list_filter = ('estado', 'buque')
    search_fields = ('chasis', 'marca', 'modelo')
    inlines = [HistorialInline]

    def save_model(self, request, obj, form, change):
        # Los cambios hechos desde /admin/ también quedan en el historial
        anterior = Vehiculo.objects.filter(pk=obj.pk).first() if change else None
        super().save_model(request, obj, form, change)
        if anterior is None:
            obj.registrar_cambio(request.user, nota='Creado desde /admin/')
        elif anterior.estado != obj.estado or (anterior.ubicacion_patio or '') != (obj.ubicacion_patio or ''):
            obj.registrar_cambio(request.user, estado_anterior=anterior.estado,
                                 ubicacion_anterior=anterior.ubicacion_patio, nota='Cambio desde /admin/')
