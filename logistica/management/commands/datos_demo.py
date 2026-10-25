"""
Carga datos de demostración: un usuario por rol, empresas, buques, camiones
y vehículos con historial. Se puede ejecutar varias veces (no duplica).

    python manage.py datos_demo
    python manage.py datos_demo --password OtraClave#2026

Solo funciona con DEBUG=True, para no crear cuentas conocidas en producción.
"""
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from logistica.models import Buque, CamionCiguena, Cliente, Vehiculo
from usuarios import roles


class Command(BaseCommand):
    help = 'Crea datos de demostración (usuarios por rol, empresas, buques y vehículos).'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='Rodamar#Demo2026',
                            help='Contraseña para las cuentas demo (por defecto: Rodamar#Demo2026)')

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Por seguridad, datos_demo solo se ejecuta con DEBUG=True.')
        password = options['password']

        hoy = date.today()
        norte, _ = Cliente.objects.get_or_create(
            rut_o_id='76.123.456-0',
            defaults={'nombre_completo': 'Automotriz del Norte SpA', 'telefono': '+56 2 2345 6789', 'email': 'contacto@autonorte.cl'},
        )
        sur, _ = Cliente.objects.get_or_create(
            rut_o_id='77.654.321-7',
            defaults={'nombre_completo': 'Comercial Sur Motors Ltda.', 'telefono': '+56 2 2987 6543', 'email': 'ventas@surmotors.cl'},
        )
        stella, _ = Buque.objects.get_or_create(
            nombre='Glovis Stella', numero_viaje='V-2026-41', defaults={'fecha_atraque': hoy - timedelta(days=3)})
        hoegh, _ = Buque.objects.get_or_create(
            nombre='Höegh Trapper', numero_viaje='V-2026-44', defaults={'fecha_atraque': hoy})
        camion, _ = CamionCiguena.objects.get_or_create(
            patente='KXTR-21', defaults={'empresa_transporte': 'Transportes del Pacífico', 'nombre_chofer': 'Pedro Soto', 'rut_chofer': '15.432.198-5'})

        cuentas = [
            ('admin_demo', roles.ADMIN, 'Alicia', 'Admin', None),
            ('empleado_demo', roles.EMPLEADO, 'Esteban', 'Empleado', None),
            ('cliente_demo', roles.CLIENTE, 'Carla', 'Cliente', norte),
        ]
        for username, rol, nombre, apellido, empresa in cuentas:
            u, creado = User.objects.get_or_create(username=username, defaults={
                'first_name': nombre, 'last_name': apellido, 'email': f'{username}@rodamar.local'})
            if creado:
                u.set_password(password)
                u.save()
            roles.asignar_rol(u, rol)
            u.perfil.empresa = empresa
            u.perfil.save()

        empleado = User.objects.get(username='empleado_demo')
        vehiculos = [
            ('JTDKB20U093456781', 'Toyota', 'Hilux', 'Blanco', stella, norte, 'ENTREGADO', 'Despachado', camion),
            ('KMHCT41BAEU123452', 'Hyundai', 'Tucson', 'Gris', stella, norte, 'EN_CAMINO', 'Bloque B - Fila 1', camion),
            ('3N1CN7AD5ZL123453', 'Nissan', 'Versa', 'Rojo', hoegh, norte, 'EN_PROCESO', 'Bloque A - Fila 3', None),
            ('MA3FB32S0K0123454', 'Suzuki', 'Swift', 'Azul', hoegh, sur, 'ENCONTRADO', 'Bloque A - Fila 1', None),
            ('LGXCE4CB5N0123455', 'BYD', 'Dolphin', 'Verde', hoegh, sur, 'ENCONTRADO', '', None),
        ]
        orden = [e for e, _ in Vehiculo.ESTADOS]
        for chasis, marca, modelo, color, buque, cliente, estado, patio, cig in vehiculos:
            v, creado = Vehiculo.objects.get_or_create(chasis=chasis, defaults={
                'marca': marca, 'modelo': modelo, 'color': color, 'buque': buque, 'cliente': cliente,
                'estado': 'ENCONTRADO', 'ubicacion_patio': 'Muelle', 'camion_ciguena': cig})
            if creado:
                v.registrar_cambio(empleado, nota='Ingreso al manifiesto (demo)')
                # Avanza estado por estado para que el historial se vea real
                for siguiente in orden[1:orden.index(estado) + 1]:
                    anterior, ub_ant = v.estado, v.ubicacion_patio
                    v.estado = siguiente
                    v.ubicacion_patio = patio
                    v.save()
                    v.registrar_cambio(empleado, estado_anterior=anterior, ubicacion_anterior=ub_ant)
                if estado == 'ENCONTRADO' and patio:
                    v.ubicacion_patio = patio
                    v.save()
                    v.registrar_cambio(empleado, estado_anterior='ENCONTRADO', ubicacion_anterior='Muelle')

        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.'))
        self.stdout.write(f'Cuentas (contraseña: {password}):')
        for username, rol, *_ in cuentas:
            self.stdout.write(f'  - {username:15} rol {roles.NOMBRE_ROL[rol]}')
        self.stdout.write('cliente_demo está vinculado a "Automotriz del Norte SpA" (3 vehículos).')
