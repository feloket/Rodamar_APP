from django.db import models

# No se define un modelo de Usuario personalizado a propósito.
#
# El proyecto usa django.contrib.auth.User (el estándar de Django) más
# Grupos (django.contrib.auth.models.Group) para diferenciar roles:
#
#   - ADMIN    -> User.is_staff=True + User.is_superuser=True (acceso a /admin/)
#   - USUARIO  -> User autenticado normal, pertenece al grupo "Operadores"
#   - INVITADO -> No tiene cuenta. Es simplemente un visitante no autenticado
#                 (AnonymousUser) que solo ve las vistas públicas.
#
# Si en el futuro se necesitan campos extra por usuario (foto, cargo,
# teléfono, etc.), ahí sí conviene evaluar un modelo de Perfil con
# OneToOneField a User, o migrar a un Custom User Model. Por ahora,
# agregarlo sería complejidad innecesaria.
