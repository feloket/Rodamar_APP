from django.contrib import admin
from django.urls import path, include
from usuarios.views import IniciarSesionView, CerrarSesionView

urlpatterns = [
    # Panel técnico de Django
    path('admin/', admin.site.urls),
    
    # Rutas públicas de inicio
    path('', include('pages.urls')),
    
    # Rutas del sistema portuario y logística
    path('logistica/', include('logistica.urls')),

    # Registro de usuarios (rol USUARIO)
    path('usuarios/', include('usuarios.urls')),
    
    # Autenticación (Login y Logout)
    # (vistas personalizadas en usuarios/views.py: "Recordarme", mensajes, etc.)
    path('login/', IniciarSesionView.as_view(), name='login'),
    path('logout/', CerrarSesionView.as_view(), name='logout'),
]