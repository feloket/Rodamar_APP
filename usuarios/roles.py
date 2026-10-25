"""
Roles del sistema RODAMAR y helpers para consultarlos.

    ADMIN    -> User.is_superuser = True (y is_staff para entrar a /admin/).
                Acceso total: crea/edita/elimina cuentas de cualquier rol.
    EMPLEADO -> Pertenece al grupo "Empleados". Opera el panel logístico,
                crea cuentas de CLIENTE y registra/edita empresas cliente.
                NO puede eliminar cuentas ni crear empleados/admins.
    CLIENTE  -> Pertenece al grupo "Clientes". Se registra solo, ve los
                vehículos de su empresa y edita SUS datos personales.
                No puede ingresar datos operativos (buques, vehículos, etc.).

Un usuario autenticado sin grupo reconocido se trata como CLIENTE
(principio de mínimo privilegio): nunca recibe permisos "por defecto".
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

ADMIN = 'admin'
EMPLEADO = 'empleado'
CLIENTE = 'cliente'

ROLES = [
    (ADMIN, 'Administrador'),
    (EMPLEADO, 'Empleado'),
    (CLIENTE, 'Cliente'),
]
NOMBRE_ROL = dict(ROLES)

GRUPO_EMPLEADOS = 'Empleados'
GRUPO_CLIENTES = 'Clientes'
# Grupo de la versión anterior del proyecto (registro público). Se limpia
# al asignar un rol nuevo.
GRUPO_LEGADO = 'Operadores'


def obtener_rol(user):
    """Devuelve 'admin', 'empleado', 'cliente' o None (visitante)."""
    if not user or not user.is_authenticated:
        return None
    # Se guarda en el objeto para no consultar los grupos varias veces por request
    if hasattr(user, '_rol_cache'):
        return user._rol_cache
    if user.is_superuser:
        rol = ADMIN
    elif user.groups.filter(name=GRUPO_EMPLEADOS).exists():
        rol = EMPLEADO
    else:
        rol = CLIENTE
    user._rol_cache = rol
    return rol


def es_admin(user):
    return obtener_rol(user) == ADMIN


def es_empleado(user):
    return obtener_rol(user) == EMPLEADO


def es_cliente(user):
    return obtener_rol(user) == CLIENTE


def es_personal(user):
    """Admin o empleado: personal interno de RODAMAR."""
    return obtener_rol(user) in (ADMIN, EMPLEADO)


def roles_que_puede_crear(user):
    """Qué roles puede asignar este usuario al crear/editar una cuenta."""
    rol = obtener_rol(user)
    if rol == ADMIN:
        return [ADMIN, EMPLEADO, CLIENTE]
    if rol == EMPLEADO:
        return [CLIENTE]
    return []


def puede_gestionar(actor, objetivo):
    """¿Puede `actor` ver/editar la cuenta `objetivo` desde Gestión de usuarios?"""
    rol_actor = obtener_rol(actor)
    if rol_actor == ADMIN:
        return True
    if rol_actor == EMPLEADO:
        return obtener_rol(objetivo) == CLIENTE
    return False


def puede_eliminar(actor, objetivo):
    """Solo un admin elimina cuentas, y nunca la suya propia."""
    return es_admin(actor) and actor.pk != objetivo.pk


def asignar_rol(user, rol):
    """Aplica el rol al usuario (flags de Django + grupos). Guarda el usuario."""
    if rol not in NOMBRE_ROL:
        raise ValueError(f'Rol desconocido: {rol}')

    user.is_superuser = rol == ADMIN
    user.is_staff = rol == ADMIN
    user.save()

    grupos_rol = Group.objects.filter(name__in=[GRUPO_EMPLEADOS, GRUPO_CLIENTES, GRUPO_LEGADO])
    user.groups.remove(*grupos_rol)
    if rol == EMPLEADO:
        user.groups.add(Group.objects.get_or_create(name=GRUPO_EMPLEADOS)[0])
    elif rol == CLIENTE:
        user.groups.add(Group.objects.get_or_create(name=GRUPO_CLIENTES)[0])

    if hasattr(user, '_rol_cache'):
        del user._rol_cache


def rol_requerido(*roles):
    """
    Decorador para vistas: exige sesión iniciada y uno de los roles indicados.
    Sin sesión -> redirige al login. Con sesión pero sin rol -> 403.

        @rol_requerido(ADMIN, EMPLEADO)
        def mi_vista(request): ...
    """
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if obtener_rol(request.user) not in roles:
                raise PermissionDenied('No tienes permisos para acceder a esta sección.')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador
