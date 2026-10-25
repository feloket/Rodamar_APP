from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.debug import sensitive_post_parameters

from . import auditoria, roles
from .limites import excede_limite
from .forms import (
    CambiarPasswordForm,
    LoginForm,
    MiPerfilForm,
    NuevaPasswordForm,
    RecuperarPasswordForm,
    RegistroForm,
    UsuarioCrearForm,
    UsuarioEditarForm,
)
from .models import Perfil, RegistroAuditoria

# Duración de la sesión cuando el usuario marca "Mantener sesión iniciada"
DURACION_RECORDARME = 60 * 60 * 24 * 14  # 14 días


def url_inicio(user):
    """Página de inicio según el rol: personal -> panel, cliente -> sus vehículos."""
    if roles.es_personal(user):
        return reverse('dashboard')
    return reverse('mis_vehiculos')


def _url_siguiente_segura(request):
    """Devuelve ?next=... solo si apunta a nuestro propio sitio (evita open redirect)."""
    siguiente = request.POST.get('next') or request.GET.get('next')
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return siguiente
    return None


def _asegurar_perfil(user):
    # Por si existe algún usuario creado antes de la migración del Perfil
    Perfil.objects.get_or_create(usuario=user)


# ---------------------------------------------------------------------------
# Registro, login y logout
# ---------------------------------------------------------------------------
@sensitive_post_parameters('password1', 'password2')
def registro_view(request):
    """
    Registro público: crea SIEMPRE una cuenta de CLIENTE.
    Las cuentas de empleado o admin solo las crea el personal autorizado
    desde Gestión de usuarios.
    """
    if request.user.is_authenticated:
        return redirect(url_inicio(request.user))

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auditoria.registrar(
                RegistroAuditoria.REGISTRO, request=request, actor=usuario,
                usuario_afectado=usuario, detalle='Registro público como cliente',
            )
            login(request, usuario)
            messages.success(request, f"¡Bienvenido, {usuario.first_name or usuario.username}! Tu cuenta de cliente fue creada.")
            return redirect(_url_siguiente_segura(request) or url_inicio(usuario))
        messages.error(request, "Revisa los datos ingresados.")
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {
        'form': form,
        'next': _url_siguiente_segura(request) or '',
    })


class IniciarSesionView(auth_views.LoginView):
    """
    Login basado en la LoginView de Django (ya maneja CSRF, ?next=,
    validación de cuenta activa y rotación del id de sesión).
    Se agrega: formulario propio, "Recordarme", redirección según rol y
    mensajes. La auditoría de login/login fallido se hace en signals.py.
    """
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        # Sin ?next=, cada rol va a su página de inicio
        return url_inicio(self.request.user)

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        if form.cleaned_data.get('recordarme'):
            self.request.session.set_expiry(DURACION_RECORDARME)
        else:
            self.request.session.set_expiry(0)  # expira al cerrar el navegador
        usuario = form.get_user()
        messages.success(self.request, f"Hola {usuario.first_name or usuario.username}, iniciaste sesión correctamente.")
        return respuesta


class CerrarSesionView(auth_views.LogoutView):
    """Logout solo por POST (la LogoutView de Django ya lo exige) + mensaje."""

    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)
        messages.info(request, "Cerraste sesión correctamente.")
        return respuesta


class CambiarPasswordView(auth_views.PasswordChangeView):
    """Cambio de contraseña para el usuario con sesión iniciada (queda auditado)."""
    template_name = 'registration/cambiar_password.html'
    form_class = CambiarPasswordForm

    def get_success_url(self):
        return reverse('mi_perfil')

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        auditoria.registrar(
            RegistroAuditoria.CAMBIO_PASSWORD, request=self.request,
            usuario_afectado=self.request.user,
        )
        messages.success(self.request, "Tu contraseña fue actualizada.")
        return respuesta


# ---------------------------------------------------------------------------
# Mi perfil (cualquier rol edita SUS datos personales, queda auditado)
# ---------------------------------------------------------------------------
@login_required
def mi_perfil(request):
    _asegurar_perfil(request.user)
    usuario = request.user

    if request.method == 'POST':
        form = MiPerfilForm(request.POST, instance=usuario)
        iniciales = form.valores_iniciales()  # antes de validar
        if form.is_valid():
            cambios = auditoria.detectar_cambios(form, iniciales)
            if cambios:
                form.save()
                auditoria.registrar_cambios(
                    RegistroAuditoria.EDICION_PERFIL, cambios,
                    request=request, usuario_afectado=usuario,
                )
                messages.success(request, f"Tus datos fueron actualizados ({len(cambios)} cambio(s) registrado(s)).")
            else:
                messages.info(request, "No hiciste cambios.")
            return redirect('mi_perfil')
        usuario.refresh_from_db()  # descarta valores inválidos en la cabecera
        messages.error(request, "Revisa los datos ingresados.")
    else:
        form = MiPerfilForm(instance=usuario)

    historial = RegistroAuditoria.objects.filter(usuario_afectado=usuario).exclude(
        accion__in=[RegistroAuditoria.LOGIN, RegistroAuditoria.LOGOUT]
    ).select_related('actor')[:15]

    return render(request, 'usuarios/mi_perfil.html', {
        'form': form,
        'historial': historial,
        'perfil': usuario.perfil,
    })


# ---------------------------------------------------------------------------
# Gestión de usuarios (admin: todas las cuentas / empleado: solo clientes)
# ---------------------------------------------------------------------------
def _usuarios_visibles(actor):
    qs = User.objects.select_related('perfil__empresa').prefetch_related('groups').order_by('username')
    if roles.es_admin(actor):
        return qs
    # Un empleado solo ve cuentas de cliente (no admins ni otros empleados)
    return qs.filter(is_superuser=False).exclude(groups__name=roles.GRUPO_EMPLEADOS)


@roles.rol_requerido(roles.ADMIN, roles.EMPLEADO)
def gestion_usuarios(request):
    q = request.GET.get('q', '').strip()
    filtro_rol = request.GET.get('rol', '')

    usuarios = _usuarios_visibles(request.user)
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(email__icontains=q) | Q(perfil__empresa__nombre_completo__icontains=q)
        )
    if roles.es_admin(request.user) and filtro_rol:
        if filtro_rol == roles.ADMIN:
            usuarios = usuarios.filter(is_superuser=True)
        elif filtro_rol == roles.EMPLEADO:
            usuarios = usuarios.filter(is_superuser=False, groups__name=roles.GRUPO_EMPLEADOS)
        elif filtro_rol == roles.CLIENTE:
            usuarios = usuarios.filter(is_superuser=False).exclude(groups__name=roles.GRUPO_EMPLEADOS)

    pagina = Paginator(usuarios.distinct(), 15).get_page(request.GET.get('page'))
    for u in pagina:
        u.rol_nombre = roles.NOMBRE_ROL[roles.obtener_rol(u)]
        u.eliminable = roles.puede_eliminar(request.user, u)

    return render(request, 'usuarios/gestion_lista.html', {
        'pagina': pagina,
        'q': q,
        'filtro_rol': filtro_rol,
        'roles_filtro': roles.ROLES,
    })


@sensitive_post_parameters('password1', 'password2')
@roles.rol_requerido(roles.ADMIN, roles.EMPLEADO)
def gestion_crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCrearForm(request.POST, actor=request.user)
        if form.is_valid():
            usuario = form.save()
            rol = roles.obtener_rol(usuario)
            auditoria.registrar(
                RegistroAuditoria.CREACION_CUENTA, request=request, usuario_afectado=usuario,
                campo='Rol', valor_nuevo=roles.NOMBRE_ROL[rol],
                detalle=f'Empresa: {usuario.perfil.empresa}' if usuario.perfil.empresa else '',
            )
            messages.success(request, f"Cuenta '{usuario.username}' creada como {roles.NOMBRE_ROL[rol]}.")
            return redirect('gestion_usuarios')
        messages.error(request, "Revisa los datos ingresados.")
    else:
        form = UsuarioCrearForm(actor=request.user, initial={'rol': roles.CLIENTE})

    return render(request, 'usuarios/gestion_form.html', {'form': form, 'creando': True})


@roles.rol_requerido(roles.ADMIN, roles.EMPLEADO)
def gestion_editar_usuario(request, pk):
    objetivo = get_object_or_404(User, pk=pk)
    if not roles.puede_gestionar(request.user, objetivo):
        raise PermissionDenied('Solo puedes gestionar cuentas de clientes.')
    _asegurar_perfil(objetivo)

    rol_anterior = roles.obtener_rol(objetivo)
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, instance=objetivo, actor=request.user)
        iniciales = form.valores_iniciales()
        if form.is_valid():
            cambios = auditoria.detectar_cambios(form, iniciales)
            form.save()
            auditoria.registrar_cambios(
                RegistroAuditoria.EDICION_CUENTA, cambios, request=request, usuario_afectado=objetivo,
            )
            rol_nuevo = roles.obtener_rol(User.objects.get(pk=objetivo.pk))
            if rol_nuevo != rol_anterior:
                auditoria.registrar(
                    RegistroAuditoria.CAMBIO_ROL, request=request, usuario_afectado=objetivo, campo='Rol',
                    valor_anterior=roles.NOMBRE_ROL[rol_anterior], valor_nuevo=roles.NOMBRE_ROL[rol_nuevo],
                )
                cambios.append(('Rol', rol_anterior, rol_nuevo))
            if cambios:
                messages.success(request, f"Cuenta '{objetivo.username}' actualizada ({len(cambios)} cambio(s)).")
            else:
                messages.info(request, "No hubo cambios.")
            return redirect('gestion_usuarios')
        messages.error(request, "Revisa los datos ingresados.")
    else:
        form = UsuarioEditarForm(instance=objetivo, actor=request.user)

    historial = RegistroAuditoria.objects.filter(usuario_afectado=objetivo).select_related('actor')[:20]
    return render(request, 'usuarios/gestion_form.html', {
        'form': form,
        'creando': False,
        'objetivo': objetivo,
        'historial': historial,
        'eliminable': roles.puede_eliminar(request.user, objetivo),
    })


@roles.rol_requerido(roles.ADMIN)
def gestion_eliminar_usuario(request, pk):
    """Solo ADMIN. GET muestra la confirmación, POST elimina."""
    objetivo = get_object_or_404(User, pk=pk)
    if not roles.puede_eliminar(request.user, objetivo):
        raise PermissionDenied('No puedes eliminar tu propia cuenta.')

    if request.method == 'POST':
        nombre = objetivo.username
        rol = roles.NOMBRE_ROL[roles.obtener_rol(objetivo)]
        # Se audita ANTES de borrar (el registro conserva el username como texto)
        auditoria.registrar(
            RegistroAuditoria.ELIMINACION_CUENTA, request=request, usuario_afectado=objetivo,
            detalle=f'Rol: {rol} · Correo: {objetivo.email}',
        )
        objetivo.delete()
        messages.success(request, f"La cuenta '{nombre}' fue eliminada.")
        return redirect('gestion_usuarios')

    return render(request, 'usuarios/gestion_eliminar.html', {'objetivo': objetivo})


# ---------------------------------------------------------------------------
# Auditoría (solo ADMIN)
# ---------------------------------------------------------------------------
@roles.rol_requerido(roles.ADMIN)
def auditoria_lista(request):
    registros = RegistroAuditoria.objects.select_related('actor', 'usuario_afectado')
    q = request.GET.get('q', '').strip()
    accion = request.GET.get('accion', '')
    if q:
        registros = registros.filter(
            Q(usuario_afectado_texto__icontains=q) | Q(actor__username__icontains=q)
            | Q(detalle__icontains=q) | Q(objeto__icontains=q) | Q(ip__icontains=q)
        )
    if accion:
        registros = registros.filter(accion=accion)

    pagina = Paginator(registros, 25).get_page(request.GET.get('page'))
    return render(request, 'usuarios/auditoria.html', {
        'pagina': pagina,
        'q': q,
        'accion': accion,
        'acciones': RegistroAuditoria.ACCIONES,
    })


# ---------------------------------------------------------------------------
# Recuperación de contraseña por correo
# Usa las vistas de Django: el enlace lleva un token de un solo uso, que
# vence (PASSWORD_RESET_TIMEOUT) y deja de servir apenas cambia la contraseña.
# En este proyecto el correo se "envía" a la consola del servidor
# (EMAIL_BACKEND de consola): nadie fuera del computador lo recibe.
# ---------------------------------------------------------------------------
RESET_MAX_POR_IP = 5
RESET_MAX_POR_CORREO = 3
RESET_VENTANA_SEGUNDOS = 60 * 60  # 1 hora


class RecuperarPasswordView(auth_views.PasswordResetView):
    template_name = 'registration/recuperar_password.html'
    email_template_name = 'registration/recuperar_password_email.txt'
    subject_template_name = 'registration/recuperar_password_asunto.txt'
    form_class = RecuperarPasswordForm

    def get_success_url(self):
        return reverse('recuperar_password_enviado')

    def form_valid(self, form):
        email = form.cleaned_data['email'].strip().lower()
        ip = auditoria.obtener_ip(self.request) or 'sin-ip'
        existe = User.objects.filter(email__iexact=email, is_active=True).exists()

        # Límite para que nadie use el formulario para llenar de correos a otro
        limitado = (excede_limite(f'reset-ip:{ip}', RESET_MAX_POR_IP, RESET_VENTANA_SEGUNDOS)
                    or excede_limite(f'reset-mail:{email}', RESET_MAX_POR_CORREO, RESET_VENTANA_SEGUNDOS))

        auditoria.registrar(
            RegistroAuditoria.RESET_SOLICITADO, request=self.request, actor=None,
            usuario_afectado=User.objects.filter(email__iexact=email).first(),
            detalle=f"Correo: {email} · cuenta {'encontrada' if existe else 'no encontrada'}"
                    f"{' · BLOQUEADO por límite' if limitado else ''}",
        )
        if limitado:
            # Misma respuesta que en un envío normal: no se revela nada
            return redirect(self.get_success_url())
        # Django solo envía el correo si la cuenta existe y está activa,
        # y la página siguiente es la misma exista o no (no revela cuentas).
        return super().form_valid(form)


class RecuperarPasswordEnviadoView(auth_views.PasswordResetDoneView):
    template_name = 'registration/recuperar_password_enviado.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Aviso de que el correo está en la terminal (solo con el backend de consola)
        contexto['correo_en_consola'] = settings.EMAIL_BACKEND.endswith(('console.EmailBackend', 'correo_consola.EmailBackend'))
        return contexto


class RecuperarPasswordConfirmarView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/recuperar_password_confirmar.html'
    form_class = NuevaPasswordForm

    def get_success_url(self):
        return reverse('recuperar_password_listo')

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        auditoria.registrar(
            RegistroAuditoria.RESET_COMPLETADO, request=self.request, actor=form.user,
            usuario_afectado=form.user,
        )
        return respuesta


class RecuperarPasswordListoView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/recuperar_password_listo.html'
