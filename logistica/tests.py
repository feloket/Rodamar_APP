from datetime import date

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from usuarios import roles

from django.core.exceptions import ValidationError

from usuarios.models import RegistroAuditoria

from .models import Buque, CamionCiguena, Cliente, HistorialEstado, Vehiculo
from .validadores import (
    calcular_dv, normalizar_patente, normalizar_rut, normalizar_vin,
    validar_patente, validar_rut, validar_vin,
)

PASSWORD = 'Muelle#Seguro2026'


def crear_usuario(username, rol):
    u = User.objects.create_user(username, f'{username}@rodamar.cl', PASSWORD)
    roles.asignar_rol(u, rol)
    return User.objects.get(pk=u.pk)


class Base(TestCase):
    def setUp(self):
        cache.clear()
        self.empleado = crear_usuario('empleado1', roles.EMPLEADO)
        self.cliente = crear_usuario('cliente1', roles.CLIENTE)
        self.empresa = Cliente.objects.create(nombre_completo='Automotriz Norte', rut_o_id='76.111.111-6')
        self.otra = Cliente.objects.create(nombre_completo='Otra SpA', rut_o_id='77.222.222-K')
        self.buque = Buque.objects.create(nombre='Glovis Stella', numero_viaje='V-1', fecha_atraque=date(2026, 10, 1))
        self.vehiculo = Vehiculo.objects.create(chasis='VIN123', marca='Toyota', modelo='Hilux',
                                                buque=self.buque, cliente=self.empresa)


class ProteccionBorradoTests(Base):
    def test_no_se_borra_buque_con_vehiculos(self):
        with self.assertRaises(ProtectedError):
            self.buque.delete()
        self.assertTrue(Vehiculo.objects.filter(pk=self.vehiculo.pk).exists())

    def test_no_se_borra_empresa_con_vehiculos(self):
        with self.assertRaises(ProtectedError):
            self.empresa.delete()

    def test_buque_sin_vehiculos_si_se_borra(self):
        vacio = Buque.objects.create(nombre='Vacío', numero_viaje='V-2', fecha_atraque=date(2026, 10, 2))
        vacio.delete()
        self.assertFalse(Buque.objects.filter(pk=vacio.pk).exists())


class HistorialEstadoTests(Base):
    def test_registrar_vehiculo_crea_historial(self):
        self.client.force_login(self.empleado)
        self.client.post(reverse('registrar_vehiculo'), {
            'chasis': 'kmhct41baeu123452', 'marca': 'Kia', 'modelo': 'Rio', 'color': '', 'buque': self.buque.pk,
            'cliente': self.empresa.pk, 'camion_ciguena': '', 'estado': 'ENCONTRADO', 'ubicacion_patio': 'A-1',
        })
        h = HistorialEstado.objects.get(vehiculo__chasis='KMHCT41BAEU123452')  # se guarda normalizado
        self.assertEqual(h.estado_nuevo, 'ENCONTRADO')
        self.assertEqual(h.usuario, self.empleado)

    def test_cambio_de_estado_queda_registrado(self):
        self.client.force_login(self.empleado)
        self.client.post(reverse('actualizar_estado', args=[self.vehiculo.pk]),
                         {'nuevo_estado': 'EN_PROCESO', 'ubicacion_patio': 'B-2'})
        h = self.vehiculo.historial.get()
        self.assertEqual((h.estado_anterior, h.estado_nuevo), ('ENCONTRADO', 'EN_PROCESO'))
        self.assertEqual((h.ubicacion_anterior, h.ubicacion_nueva), ('', 'B-2'))
        self.assertEqual(h.usuario_texto, 'empleado1')

    def test_sin_cambios_no_crea_historial(self):
        self.client.force_login(self.empleado)
        self.client.post(reverse('actualizar_estado', args=[self.vehiculo.pk]),
                         {'nuevo_estado': 'ENCONTRADO', 'ubicacion_patio': ''})
        self.assertFalse(self.vehiculo.historial.exists())

    def test_historial_se_conserva_si_se_borra_la_cuenta(self):
        self.vehiculo.registrar_cambio(self.empleado)
        self.empleado.delete()
        h = self.vehiculo.historial.get()
        self.assertIsNone(h.usuario)
        self.assertEqual(h.usuario_texto, 'empleado1')


class RastreoPrivacidadTests(Base):
    def url(self, chasis='VIN123'):
        return f"{reverse('rastreo')}?chasis={chasis}"

    def test_visitante_ve_estado_pero_no_datos_comerciales(self):
        r = self.client.get(self.url())
        self.assertContains(r, 'Toyota')
        self.assertContains(r, 'Descarga / Encontrado')
        self.assertNotContains(r, 'Automotriz Norte')
        self.assertNotContains(r, '76.111.111-6')
        self.assertNotContains(r, 'Glovis Stella')
        self.assertNotContains(r, 'Historial de estados')

    def test_cliente_de_otra_empresa_no_ve_detalle(self):
        self.cliente.perfil.empresa = self.otra
        self.cliente.perfil.save()
        self.client.force_login(self.cliente)
        self.assertNotContains(self.client.get(self.url()), '76.111.111-6')

    def test_cliente_dueno_ve_detalle_e_historial(self):
        self.cliente.perfil.empresa = self.empresa
        self.cliente.perfil.save()
        self.vehiculo.registrar_cambio(self.empleado, nota='Ingreso')
        self.client.force_login(self.cliente)
        r = self.client.get(self.url())
        self.assertContains(r, '76.111.111-6')
        self.assertContains(r, 'Historial de estados')
        self.assertNotContains(r, 'por empleado1')  # el cliente no ve quién lo movió

    def test_personal_ve_todo_incluido_quien_cambio(self):
        self.vehiculo.registrar_cambio(self.empleado, nota='Ingreso')
        self.client.force_login(self.empleado)
        r = self.client.get(self.url())
        self.assertContains(r, 'Automotriz Norte')
        self.assertContains(r, 'por empleado1')

    def test_limite_de_consultas_publicas(self):
        from . import views
        for _ in range(views.RASTREO_MAX_CONSULTAS):
            self.assertNotContains(self.client.get(self.url('NOEXISTE')), 'demasiadas consultas')
        self.assertContains(self.client.get(self.url()), 'demasiadas consultas')

    def test_personal_sin_limite(self):
        from . import views
        self.client.force_login(self.empleado)
        for _ in range(views.RASTREO_MAX_CONSULTAS + 3):
            r = self.client.get(self.url())
        self.assertNotContains(r, 'demasiadas consultas')



class ValidadoresTests(TestCase):
    def test_vin(self):
        validar_vin('JTDKB20U093456781')
        validar_vin('jtdkb20u09-3456781')  # se normaliza antes de validar
        for malo, motivo in [('JTDKB20U09345678', '16 chars'), ('JTDKB20U09345678I', 'letra I'),
                             ('JTDKB20U09345678O', 'letra O'), ('JTDKB20U0934567@1', 'símbolo')]:
            with self.assertRaises(ValidationError, msg=motivo):
                validar_vin(malo)
        self.assertEqual(normalizar_vin(' jtdkb20u093456781 '), 'JTDKB20U093456781')

    def test_rut(self):
        self.assertEqual(calcular_dv('76123456'), '0')
        self.assertEqual(calcular_dv('77222222'), 'K')
        for bueno in ['76.123.456-0', '76123456-0', '761234560', '77.222.222-k']:
            validar_rut(bueno)
        for malo in ['76.123.456-1', 'abc', '1-9', '']:
            with self.assertRaises(ValidationError):
                validar_rut(malo)
        self.assertEqual(normalizar_rut('77222222k'), '77.222.222-K')

    def test_patente(self):
        for bueno, normal in [('kxtr21', 'KXTR-21'), ('KX TR 21', 'KXTR-21'), ('ab1234', 'AB-1234'), ('AB-1234', 'AB-1234')]:
            validar_patente(bueno)
            self.assertEqual(normalizar_patente(bueno), normal)
        for malo in ['KATR21', 'ABC123', '1234AB', 'BCDF123']:  # vocal en formato nuevo, formatos inexistentes
            with self.assertRaises(ValidationError, msg=malo):
                validar_patente(malo)


class NormalizacionTests(Base):
    def test_rut_duplicado_con_otro_formato_se_rechaza(self):
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('empresa_crear'), {'nombre_completo': 'Copia', 'rut_o_id': '76111111-6'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Cliente.objects.filter(nombre_completo='Copia').count(), 0)

    def test_rut_invalido_muestra_error(self):
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('empresa_crear'), {'nombre_completo': 'Nueva', 'rut_o_id': '76.123.456-1'})
        self.assertContains(r, 'dígito verificador')

    def test_rastreo_acepta_vin_en_minusculas_y_con_guiones(self):
        v = Vehiculo.objects.create(chasis='JTDKB20U093456781', marca='Toyota', modelo='Hilux', buque=self.buque, cliente=self.empresa)
        r = self.client.get(reverse('rastreo') + '?chasis=jtdkb20u09-3456781')
        self.assertContains(r, 'VIN: JTDKB20U093456781')


class CrudPermisosTests(Base):
    def setUp(self):
        super().setUp()
        self.admin = crear_usuario('admin1', roles.ADMIN)
        self.camion = CamionCiguena.objects.create(patente='KXTR-21', empresa_transporte='Transportes')

    def test_listados_para_personal_y_403_para_cliente(self):
        for nombre in ['buques_lista', 'camiones_lista', 'vehiculos_lista', 'lista_empresas',
                       'buque_crear', 'camion_crear', 'vehiculo_crear', 'empresa_crear']:
            self.client.force_login(self.empleado)
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200, nombre)
            self.client.force_login(self.cliente)
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 403, nombre)

    def test_listados_muestran_datos(self):
        self.client.force_login(self.empleado)
        self.assertContains(self.client.get(reverse('buques_lista')), 'Glovis Stella')
        self.assertContains(self.client.get(reverse('camiones_lista')), 'KXTR-21')
        self.assertContains(self.client.get(reverse('vehiculos_lista')), 'VIN123')

    def test_filtros_de_vehiculos(self):
        Vehiculo.objects.create(chasis='OTRO1', marca='Kia', modelo='Rio', buque=self.buque, cliente=self.otra, estado='ENTREGADO')
        self.client.force_login(self.empleado)
        r = self.client.get(reverse('vehiculos_lista') + f'?empresa={self.otra.pk}')
        self.assertContains(r, 'OTRO1')
        self.assertNotContains(r, 'VIN123')
        r = self.client.get(reverse('vehiculos_lista') + '?estado=ENCONTRADO')
        self.assertContains(r, 'VIN123')
        self.assertNotContains(r, 'OTRO1')

    def test_empleado_no_ve_ni_puede_eliminar(self):
        self.client.force_login(self.empleado)
        self.assertNotContains(self.client.get(reverse('buques_lista')), 'Eliminar')
        for nombre, obj in [('buque_eliminar', self.buque), ('camion_eliminar', self.camion),
                            ('vehiculo_eliminar', self.vehiculo), ('empresa_eliminar', self.empresa)]:
            self.assertEqual(self.client.post(reverse(nombre, args=[obj.pk])).status_code, 403, nombre)

    def test_admin_no_puede_eliminar_buque_con_vehiculos(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('buque_eliminar', args=[self.buque.pk]), follow=True)
        self.assertContains(r, 'No se puede eliminar')
        self.assertTrue(Buque.objects.filter(pk=self.buque.pk).exists())

    def test_admin_elimina_vehiculo_y_queda_auditado(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('vehiculo_eliminar', args=[self.vehiculo.pk]))
        self.assertRedirects(r, reverse('vehiculos_lista'))
        self.assertFalse(Vehiculo.objects.filter(pk=self.vehiculo.pk).exists())
        reg = RegistroAuditoria.objects.get(accion='ELIMINACION_REGISTRO')
        self.assertIn('VIN123', reg.objeto)
        self.assertEqual(reg.actor, self.admin)

    def test_eliminar_camion_desasigna_vehiculos(self):
        self.vehiculo.camion_ciguena = self.camion
        self.vehiculo.save()
        self.client.force_login(self.admin)
        self.client.post(reverse('camion_eliminar', args=[self.camion.pk]))
        self.vehiculo.refresh_from_db()
        self.assertIsNone(self.vehiculo.camion_ciguena)

    def test_editar_camion_normaliza_y_audita(self):
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('camion_editar', args=[self.camion.pk]), {
            'patente': 'kxtr 21', 'empresa_transporte': 'Transportes del Sur', 'nombre_chofer': '', 'rut_chofer': '154321985',
        })
        self.assertRedirects(r, reverse('camiones_lista'))
        self.camion.refresh_from_db()
        self.assertEqual(self.camion.rut_chofer, '15.432.198-5')
        campos = set(RegistroAuditoria.objects.filter(accion='EDICION_REGISTRO').values_list('campo', flat=True))
        self.assertIn('Empresa de transporte', campos)
        self.assertIn('RUT del chofer', campos)
        self.assertNotIn('Patente Camión', campos)  # 'kxtr 21' normalizado = mismo valor, no es un cambio

    def test_editar_vehiculo_registra_historial_si_cambia_estado(self):
        self.client.force_login(self.empleado)
        datos = {'chasis': 'JTDKB20U093456781', 'marca': 'Toyota', 'modelo': 'Hilux', 'color': 'Rojo',
                 'buque': self.buque.pk, 'cliente': self.empresa.pk, 'camion_ciguena': '',
                 'estado': 'EN_PROCESO', 'ubicacion_patio': 'C-3'}
        r = self.client.post(reverse('vehiculo_editar', args=[self.vehiculo.pk]), datos)
        self.assertRedirects(r, reverse('vehiculos_lista'))
        h = self.vehiculo.historial.get()
        self.assertEqual((h.estado_anterior, h.estado_nuevo), ('ENCONTRADO', 'EN_PROCESO'))

    def test_modal_con_error_conserva_lo_escrito(self):
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('registrar_vehiculo'), {
            'chasis': 'CORTO', 'marca': 'Mazda', 'modelo': 'CX-5', 'buque': self.buque.pk,
            'cliente': self.empresa.pk, 'estado': 'ENCONTRADO',
        })
        self.assertEqual(r.status_code, 200)               # no redirige: muestra el formulario
        self.assertContains(r, 'El VIN debe tener 17 caracteres')
        self.assertContains(r, 'value="Mazda"')            # lo escrito sigue ahí
        self.assertContains(r, 'is-invalid')

    def test_bootstrap_se_sirve_localmente(self):
        r = self.client.get(reverse('home'))
        self.assertContains(r, '/static/vendor/bootstrap-5.3.3/bootstrap.min.css')
        self.assertNotContains(r, 'cdn.jsdelivr.net')



class RevisionLogicaLogisticaTests(Base):
    def test_dato_antiguo_duplicado_no_rompe_la_actualizacion_rapida(self):
        # Simula datos de antes de la normalización: 'vin-legado-1' y 'VINLEGADO1'
        Vehiculo.objects.filter(pk=self.vehiculo.pk).update(chasis='vin-legado-1')
        Vehiculo.objects.create(chasis='VINLEGADO1', marca='X', modelo='Y', buque=self.buque, cliente=self.empresa)
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('actualizar_estado', args=[self.vehiculo.pk]), {'nuevo_estado': 'EN_PROCESO', 'ubicacion_patio': ''})
        self.assertRedirects(r, reverse('dashboard'))
        self.vehiculo.refresh_from_db()
        self.assertEqual(self.vehiculo.estado, 'EN_PROCESO')

    def test_error_en_modal_de_empresas_vuelve_a_empresas(self):
        self.client.force_login(self.empleado)
        r = self.client.post(reverse('registrar_cliente'), {'nombre_completo': 'X', 'rut_o_id': '1-1', 'volver': 'empresas'})
        self.assertContains(r, 'name="volver" value="empresas"')
        r = self.client.post(reverse('registrar_cliente'), {'nombre_completo': 'X', 'rut_o_id': '76.123.456-0', 'volver': 'empresas'})
        self.assertRedirects(r, reverse('lista_empresas'))
