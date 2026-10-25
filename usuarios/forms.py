from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from logistica.models import Cliente

from . import auditoria, roles
from .models import RegistroAuditoria, validar_telefono
from .seguridad import login_bloqueado


class BootstrapErroresMixin:
    """Marca con la clase 'is-invalid' de Bootstrap los campos que tienen errores."""

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                clases = self.fields[nombre].widget.attrs.get('class', '')
                if 'is-invalid' not in clases:
                    self.fields[nombre].widget.attrs['class'] = f'{clases} is-invalid'.strip()


def validar_email_unico(email, excluir=None):
    """El User de Django no obliga a que el correo sea único: lo validamos aquí."""
    email = (email or '').strip().lower()
    qs = User.objects.filter(email__iexact=email)
    if excluir is not None:
        qs = qs.exclude(pk=excluir.pk)
    if qs.exists():
        raise forms.ValidationError('Ya existe una cuenta registrada con este correo.')
    return email


def _campo_texto(label, placeholder, required=True, max_length=150):
    return forms.CharField(
        label=label, max_length=max_length, required=required,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': placeholder}),
    )


def _campo_email():
    return forms.EmailField(
        label='Correo', required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empresa.cl'}),
    )


def _campo_telefono(required=False):
    return forms.CharField(
        label='Teléfono', max_length=20, required=required, validators=[validar_telefono],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
    )


def _estilo_passwords(form, nombres=('password1', 'password2')):
    placeholders = ['••••••••', 'Repite la contraseña']
    for nombre, ph in zip(nombres, placeholders):
        form.fields[nombre].widget.attrs.update({
            'class': 'form-control', 'placeholder': ph, 'autocomplete': 'new-password',
        })


# ---------------------------------------------------------------------------
# Registro público: SOLO crea cuentas de CLIENTE.
# El cliente no elige rol ni empresa: la empresa la vincula un empleado,
# porque es información operativa responsabilidad de RODAMAR.
# ---------------------------------------------------------------------------
class RegistroForm(BootstrapErroresMixin, UserCreationForm):
    first_name = _campo_texto('Nombre', 'Juan')
    last_name = _campo_texto('Apellido', 'Pérez')
    email = _campo_email()
    telefono = _campo_telefono()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario', 'autofocus': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _estilo_passwords(self)

    def clean_email(self):
        return validar_email_unico(self.cleaned_data['email'])

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        # El registro público nunca crea personal interno
        usuario.is_staff = False
        usuario.is_superuser = False
        if commit:
            usuario.save()  # la señal post_save crea el Perfil
            usuario.perfil.telefono = self.cleaned_data.get('telefono', '')
            usuario.perfil.save()
            roles.asignar_rol(usuario, roles.CLIENTE)
        return usuario


# Formulario de login. Extiende AuthenticationForm (que ya valida usuario,
# contraseña y que la cuenta esté activa) y agrega "Recordarme".
class LoginForm(BootstrapErroresMixin, AuthenticationForm):
    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Usuario o correo',
            'autofocus': True,
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
    )
    recordarme = forms.BooleanField(
        label='Mantener sesión iniciada',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    error_messages = {
        'invalid_login': 'Usuario o contraseña incorrectos.',
        'inactive': 'Esta cuenta está desactivada. Contacta a un administrador.',
    }

    def clean(self):
        # Permite iniciar sesión con el correo además del nombre de usuario
        username = self.cleaned_data.get('username', '')
        if '@' in username:
            usuario = User.objects.filter(email__iexact=username.strip()).first()
            if usuario:
                self.cleaned_data['username'] = usuario.get_username()

        # Bloqueo por fuerza bruta: se revisa ANTES de verificar la contraseña
        ip = auditoria.obtener_ip(self.request)
        bloqueado, minutos = login_bloqueado(self.cleaned_data.get('username'), ip)
        if bloqueado:
            auditoria.registrar(
                RegistroAuditoria.LOGIN_BLOQUEADO, request=self.request, actor=None,
                usuario_texto=self.cleaned_data.get('username', ''),
            )
            raise forms.ValidationError(
                f'Demasiados intentos fallidos. Por seguridad el acceso está bloqueado '
                f'por {minutos} minutos. Si olvidaste tu contraseña, puedes recuperarla.',
                code='bloqueado',
            )
        return super().clean()


# Cambio de contraseña con estilos Bootstrap.
class CambiarPasswordForm(BootstrapErroresMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ---------------------------------------------------------------------------
# "Mi perfil": cada usuario edita SOLO sus datos personales.
# Rol, empresa y estado de la cuenta no aparecen aquí.
# ---------------------------------------------------------------------------
class MiPerfilForm(BootstrapErroresMixin, forms.ModelForm):
    first_name = _campo_texto('Nombre', 'Juan')
    last_name = _campo_texto('Apellido', 'Pérez')
    email = _campo_email()
    telefono = _campo_telefono()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    password_actual = forms.CharField(
        label='Contraseña actual', required=False, strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
        help_text='Solo es obligatoria si cambias tu correo.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefono'].initial = self.instance.perfil.telefono
        # Se guarda el correo original ANTES de validar (el ModelForm cambia la instancia al validar)
        self._email_original = (self.instance.email or '').lower()

    def clean_email(self):
        return validar_email_unico(self.cleaned_data['email'], excluir=self.instance)

    def clean(self):
        datos = super().clean()
        # Cambiar el correo permite recuperar la contraseña con él, así que se
        # pide la contraseña actual: si alguien encuentra la sesión abierta,
        # no puede quedarse con la cuenta.
        email = datos.get('email')
        if email and email != self._email_original:
            if not self.instance.check_password(datos.get('password_actual') or ''):
                self.add_error('password_actual', 'Para cambiar el correo ingresa tu contraseña actual.')
        return datos

    def valores_iniciales(self):
        u = self.instance
        return {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'telefono': u.perfil.telefono,
        }

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.perfil.telefono = self.cleaned_data.get('telefono', '')
            usuario.perfil.save()
        return usuario


# ---------------------------------------------------------------------------
# Gestión de cuentas por el personal (admin / empleado)
# ---------------------------------------------------------------------------
class _CamposGestionMixin:
    """Campos comunes y reglas de rol para crear/editar cuentas desde el panel."""

    def _preparar(self, actor):
        self.actor = actor
        permitidos = roles.roles_que_puede_crear(actor)
        self.fields['rol'].choices = [(r, roles.NOMBRE_ROL[r]) for r in permitidos]
        self.fields['empresa'].queryset = Cliente.objects.order_by('nombre_completo')

    def clean_rol(self):
        rol = self.cleaned_data['rol']
        # Doble validación en el servidor: aunque alguien manipule el HTML,
        # un empleado no puede crear empleados ni administradores.
        if rol not in roles.roles_que_puede_crear(self.actor):
            raise forms.ValidationError('No tienes permiso para asignar ese rol.')
        return rol

    def clean(self):
        datos = super().clean()
        # La empresa solo tiene sentido para cuentas de cliente
        if datos.get('rol') and datos.get('rol') != roles.CLIENTE:
            datos['empresa'] = None
        return datos


def _campo_rol():
    return forms.ChoiceField(label='Rol', widget=forms.Select(attrs={'class': 'form-select'}))


def _campo_empresa():
    return forms.ModelChoiceField(
        label='Empresa cliente', queryset=Cliente.objects.none(), required=False,
        empty_label='— Sin empresa asignada —',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Solo para cuentas de cliente: define qué vehículos puede ver.',
    )


class UsuarioCrearForm(BootstrapErroresMixin, _CamposGestionMixin, UserCreationForm):
    first_name = _campo_texto('Nombre', 'Juan')
    last_name = _campo_texto('Apellido', 'Pérez')
    email = _campo_email()
    telefono = _campo_telefono()
    rol = _campo_rol()
    empresa = _campo_empresa()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._preparar(actor)
        _estilo_passwords(self)

    def clean_email(self):
        return validar_email_unico(self.cleaned_data['email'])

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.save()
        usuario.perfil.telefono = self.cleaned_data.get('telefono', '')
        usuario.perfil.empresa = self.cleaned_data.get('empresa')
        usuario.perfil.save()
        roles.asignar_rol(usuario, self.cleaned_data['rol'])
        return usuario


class UsuarioEditarForm(BootstrapErroresMixin, _CamposGestionMixin, forms.ModelForm):
    first_name = _campo_texto('Nombre', 'Juan')
    last_name = _campo_texto('Apellido', 'Pérez')
    email = _campo_email()
    telefono = _campo_telefono()
    rol = _campo_rol()
    empresa = _campo_empresa()
    is_active = forms.BooleanField(
        label='Cuenta activa', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Una cuenta inactiva no puede iniciar sesión.',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._preparar(actor)
        u = self.instance
        self.fields['telefono'].initial = u.perfil.telefono
        self.fields['empresa'].initial = u.perfil.empresa_id
        self.fields['rol'].initial = roles.obtener_rol(u)

        # Solo un admin cambia roles o desactiva cuentas, y nunca la propia
        # (evita que el sistema se quede sin administradores por error).
        if not roles.es_admin(actor) or actor.pk == u.pk:
            del self.fields['is_active']
            self.fields['rol'].disabled = True
            self.fields['rol'].choices = [(self.fields['rol'].initial, roles.NOMBRE_ROL[self.fields['rol'].initial])]

    def clean_rol(self):
        if self.fields['rol'].disabled:
            return self.fields['rol'].initial
        return super().clean_rol()

    def clean_email(self):
        return validar_email_unico(self.cleaned_data['email'], excluir=self.instance)

    def valores_iniciales(self):
        u = self.instance
        valores = {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'telefono': u.perfil.telefono,
            'empresa': u.perfil.empresa,
        }
        if 'is_active' in self.fields:
            valores['is_active'] = u.is_active
        return valores

    def save(self, commit=True):
        usuario = super().save()
        usuario.perfil.telefono = self.cleaned_data.get('telefono', '')
        usuario.perfil.empresa = self.cleaned_data.get('empresa')
        usuario.perfil.save()
        if not self.fields['rol'].disabled:
            roles.asignar_rol(usuario, self.cleaned_data['rol'])
        return usuario


# ---------------------------------------------------------------------------
# Recuperación de contraseña por correo (vistas estándar de Django)
# ---------------------------------------------------------------------------
class RecuperarPasswordForm(BootstrapErroresMixin, PasswordResetForm):
    email = forms.EmailField(
        label='Correo de tu cuenta', max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg', 'placeholder': 'correo@empresa.cl',
            'autocomplete': 'email', 'autofocus': True,
        }),
    )


class NuevaPasswordForm(BootstrapErroresMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
