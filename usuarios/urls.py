from django.urls import path

from . import views

urlpatterns = [
    # Público
    path('registro/', views.registro_view, name='registro'),

    # Confirmación del correo de una cuenta nueva
    path('confirmar/enviado/', views.confirmacion_enviada, name='confirmacion_enviada'),
    path('confirmar/reenviar/', views.reenviar_confirmacion, name='reenviar_confirmacion'),
    path('confirmar/<str:token>/', views.confirmar_correo, name='confirmar_correo'),

    # Recuperación de contraseña por correo
    path('recuperar/', views.RecuperarPasswordView.as_view(), name='recuperar_password'),
    path('recuperar/enviado/', views.RecuperarPasswordEnviadoView.as_view(), name='recuperar_password_enviado'),
    path('recuperar/<uidb64>/<token>/', views.RecuperarPasswordConfirmarView.as_view(), name='recuperar_password_confirmar'),
    path('recuperar/listo/', views.RecuperarPasswordListoView.as_view(), name='recuperar_password_listo'),

    # Cualquier usuario con sesión
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('cambiar-password/', views.CambiarPasswordView.as_view(), name='cambiar_password'),

    # Solo admin
    path('gestion/', views.gestion_usuarios, name='gestion_usuarios'),
    path('gestion/nuevo/', views.gestion_crear_usuario, name='gestion_crear_usuario'),
    path('gestion/<int:pk>/editar/', views.gestion_editar_usuario, name='gestion_editar_usuario'),
    path('gestion/<int:pk>/eliminar/', views.gestion_eliminar_usuario, name='gestion_eliminar_usuario'),
    path('auditoria/', views.auditoria_lista, name='auditoria'),
]
