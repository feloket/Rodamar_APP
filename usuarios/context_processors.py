from . import roles


def rol_usuario(request):
    """Expone el rol a todas las plantillas: {{ rol }}, {% if es_admin %}, etc."""
    rol = roles.obtener_rol(request.user)
    return {
        'rol': rol,
        'rol_nombre': roles.NOMBRE_ROL.get(rol, 'Invitado'),
        'es_admin': rol == roles.ADMIN,
        'es_empleado': rol == roles.EMPLEADO,
        'es_cliente': rol == roles.CLIENTE,
        'es_personal': rol in (roles.ADMIN, roles.EMPLEADO),
    }
