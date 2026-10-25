from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    verbose_name = 'Usuarios y Roles'

    def ready(self):
        # Conecta las señales (perfil automático y auditoría de sesiones)
        from . import signals  # noqa: F401
