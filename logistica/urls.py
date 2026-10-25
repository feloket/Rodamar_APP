from django.urls import path
from . import views, views_crud

urlpatterns = [
    path('rastreo/', views.rastreo_vehiculo, name='rastreo'),
    path('panel/', views.dashboard_operaciones, name='dashboard'),
    path('panel/nuevo-vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('panel/nuevo-buque/', views.registrar_buque, name='registrar_buque'),
    path('panel/nuevo-cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('panel/nuevo-camion/', views.registrar_camion, name='registrar_camion'),
    path('panel/actualizar/<int:pk>/', views.actualizar_estado_vehiculo, name='actualizar_estado'),
    path('empresas/', views.lista_empresas, name='lista_empresas'),
    path('empresas/<int:pk>/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresas/nueva/', views_crud.empresa_crear, name='empresa_crear'),
    path('empresas/<int:pk>/eliminar/', views_crud.empresa_eliminar, name='empresa_eliminar'),
    path('mis-vehiculos/', views.mis_vehiculos, name='mis_vehiculos'),

    # CRUD de buques, camiones y vehículos (eliminar: solo admin)
    path('buques/', views_crud.buques_lista, name='buques_lista'),
    path('buques/nuevo/', views_crud.buque_crear, name='buque_crear'),
    path('buques/<int:pk>/editar/', views_crud.buque_editar, name='buque_editar'),
    path('buques/<int:pk>/eliminar/', views_crud.buque_eliminar, name='buque_eliminar'),

    path('camiones/', views_crud.camiones_lista, name='camiones_lista'),
    path('camiones/nuevo/', views_crud.camion_crear, name='camion_crear'),
    path('camiones/<int:pk>/editar/', views_crud.camion_editar, name='camion_editar'),
    path('camiones/<int:pk>/eliminar/', views_crud.camion_eliminar, name='camion_eliminar'),

    path('vehiculos/', views_crud.vehiculos_lista, name='vehiculos_lista'),
    path('vehiculos/nuevo/', views_crud.vehiculo_crear, name='vehiculo_crear'),
    path('vehiculos/<int:pk>/editar/', views_crud.vehiculo_editar, name='vehiculo_editar'),
    path('vehiculos/<int:pk>/eliminar/', views_crud.vehiculo_eliminar, name='vehiculo_eliminar'),
]