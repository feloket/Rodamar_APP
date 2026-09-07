from django.contrib import admin

# No es necesario registrar nada aquí: django.contrib.auth ya registra
# User y Group en /admin/ automáticamente. Desde ahí un ADMIN puede:
#   - Marcar/desmarcar "Staff status" y "Superuser status" de cualquier
#     usuario (esto es lo que define el rol ADMIN).
#   - Ver y editar a qué grupo ("Operadores") pertenece cada usuario.
