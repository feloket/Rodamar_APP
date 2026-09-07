from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Formulario de registro para el rol USUARIO (operador autenticado normal).
# Extiende el UserCreationForm de Django, que ya trae validación de
# contraseñas (fuerza, confirmación, etc.) definida en AUTH_PASSWORD_VALIDATORS.
class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empresa.cl'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # UserCreationForm no aplica clases de Bootstrap a password1/password2
        # por defecto, así que se agregan aquí.
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Repite la contraseña'
        })
