from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Panel técnico de Django
    path('admin/', admin.site.urls),
    
    # Rutas públicas de inicio
    path('', include('pages.urls')),
    
    # Rutas del sistema portuario y logística
    path('logistica/', include('logistica.urls')),
    
    # Autenticación (Login y Logout)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]