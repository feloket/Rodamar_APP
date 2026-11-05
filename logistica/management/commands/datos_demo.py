"""
Carga datos de muestra: cuentas por rol, empresas, buques, camiones y vehículos
con su historial de estados. Se puede ejecutar varias veces (no duplica).

    python manage.py datos_demo
    python manage.py datos_demo --password OtraClave#2026

Solo funciona con DEBUG=True, para no crear cuentas conocidas en producción.
Todos los nombres, RUT, patentes y correos son inventados.
"""
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from logistica.models import Buque, CamionCiguena, Cliente, HistorialEstado, Vehiculo
from logistica.validadores import calcular_dv, normalizar_rut
from usuarios import roles


def rut(cuerpo):
    return normalizar_rut(f'{cuerpo}{calcular_dv(cuerpo)}')


EMPRESAS = [
    ('norte', 'Automotriz del Norte SpA', rut(76123456), '+56 2 2345 6789', 'contacto@autonorte.example'),
    ('sur', 'Comercial Sur Motors Ltda.', rut(77654321), '+56 2 2987 6543', 'ventas@surmotors.example'),
    ('pacifico', 'Importadora Pacífico S.A.', rut(76900123), '+56 57 241 5500', 'operaciones@imppacifico.example'),
    ('andes', 'Andes Vehículos Comerciales SpA', rut(77310450), '+56 55 228 1400', 'flota@andesvc.example'),
    ('tamarugal', 'Distribuidora Tamarugal Ltda.', rut(76458213), '+56 57 276 3300', 'contacto@tamarugal.example'),
    ('sinvehiculos', 'Rent a Car Costa Brava SpA', rut(77888123), '', 'admin@costabrava.example'),
]
# clave, nombre, viaje, días desde el atraque
BUQUES = [
    ('stella', 'Glovis Stella', 'V-2026-41', 34),
    ('trapper', 'Höegh Trapper', 'V-2026-44', 16),
    ('morning', 'Morning Celesta', 'V-2026-47', 7),
    ('auriga', 'Auriga Leader', 'V-2026-52', 1),
    ('futuro', 'Grande Santiago', 'V-2026-55', -6),  # todavía no atraca: sin vehículos
]
CAMIONES = [
    ('kxtr', 'KXTR-21', 'Transportes del Pacífico', 'Pedro Soto', rut(15432198)),
    ('hjlp', 'HJLP-48', 'Transportes del Pacífico', 'Marcela Rojas', rut(13876540)),
    ('wbxd', 'WBXD-73', 'Logística Atacama', 'Ricardo Araya', rut(16204771)),
    ('cz', 'CZ-4471', 'Cigüeñas del Sur', '', None),
]
# usuario, rol, nombre, apellido, empresa, correo confirmado
CUENTAS = [
    ('admin_demo', roles.ADMIN, 'Alicia', 'Admin', None, True),
    ('empleado_demo', roles.EMPLEADO, 'Esteban', 'Empleado', None, True),
    ('empleado2_demo', roles.EMPLEADO, 'Paula', 'Muñoz', None, True),
    ('cliente_demo', roles.CLIENTE, 'Carla', 'Cliente', 'norte', True),
    ('cliente_sur_demo', roles.CLIENTE, 'Sergio', 'Vidal', 'sur', True),
    ('cliente_sinempresa_demo', roles.CLIENTE, 'Nora', 'Pizarro', None, True),
    ('cliente_pendiente_demo', roles.CLIENTE, 'Iván', 'Castro', None, False),
]
MODELOS = [
    ('Toyota', 'Hilux', 'JTD'), ('Hyundai', 'Tucson', 'KMH'), ('Nissan', 'Versa', '3N1'),
    ('Suzuki', 'Swift', 'MA3'), ('BYD', 'Dolphin', 'LGX'), ('Kia', 'Sportage', 'KNA'),
    ('Chevrolet', 'Sail', 'LSG'), ('MG', 'ZS', 'LSJ'), ('Mazda', 'CX-5', 'JM1'),
]
COLORES = ['Blanco', 'Gris', 'Rojo', 'Azul', 'Negro', 'Plata', 'Verde']
# buque, empresa, cantidades por estado (encontrado, inspección, traslado, entregado)
LOTES = [
    ('stella', 'norte', (0, 0, 1, 5)),
    ('stella', 'pacifico', (0, 0, 0, 4)),
    ('trapper', 'sur', (0, 1, 2, 3)),
    ('trapper', 'andes', (0, 2, 1, 2)),
    ('morning', 'norte', (1, 3, 1, 0)),
    ('morning', 'tamarugal', (2, 2, 0, 0)),
    ('auriga', 'sur', (4, 1, 0, 0)),
    ('auriga', 'pacifico', (5, 0, 0, 0)),
]


class Command(BaseCommand):
    help = 'Crea datos de muestra (cuentas por rol, empresas, buques, camiones y vehículos).'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='Rodamar#Demo2026',
                            help='Contraseña para las cuentas demo (por defecto: Rodamar#Demo2026)')

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Por seguridad, datos_demo solo se ejecuta con DEBUG=True.')

        empresas = self._empresas()
        buques = self._buques()
        camiones = self._camiones()
        self._cuentas(empresas, options['password'])
        self._vehiculos(empresas, buques, camiones)

        self.stdout.write(self.style.SUCCESS('Datos de muestra listos.'))
        self.stdout.write(
            f'{Cliente.objects.count()} empresas, {Buque.objects.count()} buques, '
            f'{CamionCiguena.objects.count()} camiones, {Vehiculo.objects.count()} vehículos, '
            f'{HistorialEstado.objects.count()} movimientos de historial.'
        )
        self.stdout.write(f'Cuentas (contraseña: {options["password"]}):')
        for username, rol, *_ in CUENTAS:
            self.stdout.write(f'  - {username:25} {roles.NOMBRE_ROL[rol]}')

    @staticmethod
    def _crear(modelo, buscar, valores):
        """Valida con las mismas reglas del sitio: un dato de muestra inválido falla aquí."""
        objeto = modelo.objects.filter(**buscar).first()
        if objeto is None:
            objeto = modelo(**buscar, **valores)
            objeto.full_clean()
            objeto.save()
        return objeto

    def _empresas(self):
        return {
            clave: self._crear(Cliente, {'rut_o_id': r},
                               {'nombre_completo': nombre, 'telefono': telefono, 'email': email})
            for clave, nombre, r, telefono, email in EMPRESAS
        }

    def _buques(self):
        hoy = date.today()
        return {
            clave: self._crear(Buque, {'nombre': nombre, 'numero_viaje': viaje},
                               {'fecha_atraque': hoy - timedelta(days=dias)})
            for clave, nombre, viaje, dias in BUQUES
        }

    def _camiones(self):
        return {
            clave: self._crear(CamionCiguena, {'patente': patente}, {
                'empresa_transporte': empresa, 'nombre_chofer': chofer, 'rut_chofer': rut_chofer})
            for clave, patente, empresa, chofer, rut_chofer in CAMIONES
        }

    def _cuentas(self, empresas, password):
        for username, rol, nombre, apellido, empresa, confirmado in CUENTAS:
            usuario, creado = User.objects.get_or_create(username=username, defaults={
                'first_name': nombre, 'last_name': apellido, 'email': f'{username}@rodamar.example'})
            if creado:
                usuario.set_password(password)
                usuario.save()
            roles.asignar_rol(usuario, rol)
            usuario.perfil.empresa = empresas[empresa] if empresa else None
            usuario.perfil.email_confirmado = confirmado
            usuario.perfil.telefono = f'+56 9 5555 {1000 + usuario.pk}'
            usuario.perfil.save()

    def _vehiculos(self, empresas, buques, camiones):
        orden = [estado for estado, _ in Vehiculo.ESTADOS]
        operadores = list(User.objects.filter(username__in=['empleado_demo', 'empleado2_demo']).order_by('username'))
        lista_camiones = list(camiones.values())
        ahora = timezone.now()
        fijo = 'JTDKB20U093456781'  # chasis de ejemplo del README (empresa de cliente_demo)
        n = 0
        for clave_buque, clave_empresa, cantidades in LOTES:
            buque, empresa = buques[clave_buque], empresas[clave_empresa]
            dias_lote = (date.today() - buque.fecha_atraque).days
            for indice_estado, cantidad in enumerate(cantidades):
                for _ in range(cantidad):
                    marca, modelo, wmi = MODELOS[n % len(MODELOS)]
                    chasis = fijo if n == 0 else f'{wmi}RDM7{n:010d}'
                    self._vehiculo(chasis, marca, modelo, COLORES[n % len(COLORES)], buque, empresa,
                                   orden[indice_estado], lista_camiones[n % len(lista_camiones)],
                                   operadores[n % 2], n, dias_lote, ahora, orden)
                    n += 1

    def _vehiculo(self, chasis, marca, modelo, color, buque, empresa, estado, camion, operador, n, dias, ahora, orden):
        if Vehiculo.objects.filter(chasis=chasis).exists():
            return
        necesita_camion = estado in ('EN_CAMINO', 'ENTREGADO')
        patio_final = {
            'ENCONTRADO': f'Muelle Norte - Zona {n % 4 + 1}',
            'EN_PROCESO': f'Bloque A - Fila {n % 9 + 1}',
            'EN_CAMINO': f'Bloque B - Fila {n % 6 + 1}',
            'ENTREGADO': 'Despachado',
        }[estado]
        v = Vehiculo(chasis=chasis, marca=marca, modelo=modelo, color=color, buque=buque, cliente=empresa,
                     estado=orden[0], ubicacion_patio=f'Muelle Norte - Zona {n % 4 + 1}',
                     camion_ciguena=camion if necesita_camion else None)
        v.full_clean()
        v.save()
        # Fechas repartidas desde el atraque para que el historial se vea real
        pasos = orden.index(estado)
        fechas = [ahora - timedelta(days=dias) + timedelta(hours=8 + i * max(dias, 1) * 24 // (pasos + 1) + n % 5)
                  for i in range(pasos + 1)]
        registro = v.registrar_cambio(operador, nota='Ingreso al manifiesto')
        HistorialEstado.objects.filter(pk=registro.pk).update(fecha=min(fechas[0], ahora))
        for siguiente, fecha in zip(orden[1:pasos + 1], fechas[1:]):
            anterior, ubicacion_anterior = v.estado, v.ubicacion_patio
            v.estado, v.ubicacion_patio = siguiente, patio_final
            v.save()
            registro = v.registrar_cambio(operador, estado_anterior=anterior, ubicacion_anterior=ubicacion_anterior)
            HistorialEstado.objects.filter(pk=registro.pk).update(fecha=min(fecha, ahora))
        Vehiculo.objects.filter(pk=v.pk).update(fecha_registro=min(fechas[0], ahora))
