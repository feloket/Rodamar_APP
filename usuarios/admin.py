from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Perfil, RegistroAuditoria


# Muestra teléfono y empresa dentro de la ficha del usuario en /admin/
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    extra = 0
    autocomplete_fields = ['empresa']


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_active')


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    """Solo lectura: la bitácora no se puede crear, editar ni borrar a mano."""
    list_display = ('fecha', 'accion', 'actor', 'usuario_afectado_texto', 'campo', 'valor_anterior', 'valor_nuevo', 'ip')
    list_filter = ('accion', 'fecha')
    search_fields = ('usuario_afectado_texto', 'actor__username', 'detalle', 'objeto', 'ip')
    # Ojo: no usar date_hierarchy aquí. Con USE_TZ=True necesita las tablas de
    # zona horaria de MySQL, que en Windows normalmente no vienen instaladas
    # (la página daba error 500). El filtro por fecha de la derecha sí funciona.

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
