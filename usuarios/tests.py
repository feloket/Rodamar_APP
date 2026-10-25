from datetime import date

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from logistica.models import Buque, Cliente, Vehiculo

from . import roles
from .models import RegistroAuditoria

PASSWORD = 'Muelle#Seguro2026'


def crear_usuario(username, rol, **extra):
    u = User.objects.create_user(username, f'{username}@rodamar.cl', PASSWORD, **extra)
    roles.asignar_rol(u, rol)
    return User.objects.get(pk=u.pk)


class BaseRoles(TestCase):
    def setUp(self):
        self.admin = crear_usuario('admin1', roles.ADMIN)
        self.empleado = crear_usuario('empleado1', roles.EMPLEADO)
        self.cliente = crear_usuario('cliente1', roles.CLIENTE, first_name='Ana')
        self.empresa = Cliente.objects.create(nombre_completo='Automotriz Norte', rut_o_id='76.111.111-6')

    def entrar(self, user):
        self.client.force_login(user)


# ---------------------------------------------------------------------------
# Registro público -> siempre CLIENTE
# ---------------------------------------------------------------------------
class RegistroTests(TestCase):
    def datos(self, **extra):
        datos = {
            'username': 'nuevo', 'first_name': 'Juan', 'last_name': 'Pérez',
            'email': 'Juan@Empresa.cl', 'telefono': '+56 9 1234 5678',
            'password1': PASSWORD, 'password2': PASSWORD,
        }
        datos.update(extra)
        return datos

    def test_registro_crea_cliente(self):
        r = self.client.post(reverse('registro'), self.datos())
        self.assertRedirects(r, reverse('mis_vehiculos'))
        u = User.objects.get(username='nuevo')
        self.assertEqual(roles.obtener_rol(u), roles.CLIENTE)
        self.assertFalse(u.is_staff or u.is_superuser)
        self.assertEqual(u.email, 'juan@empresa.cl')
        self.assertEqual(u.perfil.telefono, '+56 9 1234 5678')
        self.assertIsNone(u.perfil.empresa)  # la empresa la asigna un empleado
        self.assertTrue(RegistroAuditoria.objects.filter(accion='REGISTRO', usuario_afectado=u).exists())

    def test_registro_ignora_intentos_de_escalar_privilegios(self):
        self.client.post(reverse('registro'), self.datos(is_superuser='on', is_staff='on', rol='admin'))
        u = User.objects.get(username='nuevo')
        self.assertEqual(roles.obtener_rol(u), roles.CLIENTE)

    def test_correo_repetido(self):
        User.objects.create_user('otro', 'juan@empresa.cl', PASSWORD)
        r = self.client.post(reverse('registro'), self.datos())
        self.assertContains(r, 'Ya existe una cuenta registrada con este correo.')

    def test_telefono_invalido(self):
        r = self.client.post(reverse('registro'), self.datos(telefono='abc'))
        self.assertContains(r, 'Ingresa un teléfono válido')


# ---------------------------------------------------------------------------
# Login / logout / navbar
# ---------------------------------------------------------------------------
class LoginLogoutTests(BaseRoles):
    def login(self, username, **extra):
        return self.client.post(reverse('login'), {'username': username, 'password': PASSWORD, **extra})

    def test_login_redirige_segun_rol(self):
        self.assertRedirects(self.login('cliente1'), reverse('mis_vehiculos'))
        self.client.logout()
        self.assertRedirects(self.login('empleado1'), reverse('dashboard'))
        self.client.logout()
        self.assertRedirects(self.login('admin1'), reverse('dashboard'))

    def test_login_con_correo(self):
        self.assertRedirects(self.login('CLIENTE1@rodamar.cl'), reverse('mis_vehiculos'))

    def test_login_incorrecto_queda_auditado(self):
        r = self.client.post(reverse('login'), {'username': 'cliente1', 'password': 'mala'})
        self.assertContains(r, 'Usuario o contraseña incorrectos.')
        registro = RegistroAuditoria.objects.get(accion='LOGIN_FALLIDO')
        self.assertIn('cliente1', registro.detalle)
        self.assertNotIn('mala', registro.detalle)  # nunca se guarda la contraseña

    def test_login_y_logout_auditados(self):
        self.login('cliente1')
        self.client.post(reverse('logout'))
        acciones = list(RegistroAuditoria.objects.filter(usuario_afectado=self.cliente).values_list('accion', flat=True))
        self.assertIn('LOGIN', acciones)
        self.assertIn('LOGOUT', acciones)

    def test_login_ignora_next_externo(self):
        self.assertRedirects(self.login('empleado1', next='https://malo.com/'), reverse('dashboard'))

    def test_recordarme(self):
        self.login('cliente1', recordarme='on')
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.client.logout()
        self.login('cliente1')
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_logout_solo_post(self):
        self.entrar(self.cliente)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        r = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(r, reverse('home'))
        self.assertContains(r, 'Cerraste sesión correctamente.')

    def test_navbar_visitante_en_todas_las_paginas(self):
        for url in [reverse('home'), reverse('rastreo'), reverse('registro'), reverse('login')]:
            r = self.client.get(url)
            self.assertContains(r, 'Iniciar sesión', msg_prefix=url)
            self.assertContains(r, 'Crear cuenta', msg_prefix=url)
            self.assertNotContains(r, 'Cerrar sesión', msg_prefix=url)

    def test_navbar_cliente(self):
        self.entrar(self.cliente)
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Cerrar sesión')
        self.assertContains(r, 'Mis vehículos')
        self.assertContains(r, 'Mis datos')
        self.assertNotContains(r, reverse('dashboard'))
        self.assertNotContains(r, reverse('gestion_usuarios'))
        self.assertNotContains(r, reverse('auditoria'))

    def test_navbar_empleado(self):
        self.entrar(self.empleado)
        r = self.client.get(reverse('home'))
        self.assertContains(r, reverse('dashboard'))
        self.assertContains(r, 'Cuentas cliente')
        self.assertNotContains(r, reverse('auditoria'))
        self.assertNotContains(r, 'Admin de Django')

    def test_navbar_admin(self):
        self.entrar(self.admin)
        r = self.client.get(reverse('home'))
        self.assertContains(r, reverse('auditoria'))
        self.assertContains(r, 'Admin de Django')

    def test_navbar_tiene_modo_noche_y_accesibilidad(self):
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'id="btn-tema"')
        self.assertContains(r, 'id="acc-fuente-mas"')
        self.assertContains(r, 'id="acc-fuente-menos"')


# ---------------------------------------------------------------------------
# Permisos por rol en las vistas
# ---------------------------------------------------------------------------
class PermisosTests(BaseRoles):
    def test_cliente_no_entra_a_vistas_operativas(self):
        self.entrar(self.cliente)
        for nombre in ['dashboard', 'lista_empresas', 'gestion_usuarios', 'gestion_crear_usuario', 'auditoria']:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 403, nombre)

    def test_cliente_no_puede_ingresar_datos_operativos(self):
        self.entrar(self.cliente)
        r = self.client.post(reverse('registrar_buque'), {'nombre': 'X', 'numero_viaje': '1', 'fecha_atraque': '2026-10-01'})
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Buque.objects.exists())
        r = self.client.post(reverse('registrar_cliente'), {'nombre_completo': 'X', 'rut_o_id': '1-9'})
        self.assertEqual(r.status_code, 403)

    def test_visitante_va_al_login(self):
        r = self.client.get(reverse('dashboard'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_empleado_opera_panel_pero_no_ve_auditoria(self):
        self.entrar(self.empleado)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('lista_empresas')).status_code, 200)
        self.assertEqual(self.client.get(reverse('auditoria')).status_code, 403)

    def test_estado_de_vehiculo_invalido(self):
        buque = Buque.objects.create(nombre='B', numero_viaje='1', fecha_atraque=date(2026, 10, 1))
        v = Vehiculo.objects.create(chasis='VIN1', marca='M', modelo='X', buque=buque, cliente=self.empresa)
        self.entrar(self.empleado)
        self.client.post(reverse('actualizar_estado', args=[v.pk]), {'nuevo_estado': 'HACKEADO'})
        v.refresh_from_db()
        self.assertEqual(v.estado, 'ENCONTRADO')


# ---------------------------------------------------------------------------
# Gestión de cuentas
# ---------------------------------------------------------------------------
class GestionCuentasTests(BaseRoles):
    def datos_nueva(self, rol, **extra):
        datos = {
            'username': 'nueva', 'first_name': 'N', 'last_name': 'C', 'email': 'nueva@x.cl',
            'telefono': '', 'rol': rol, 'empresa': self.empresa.pk,
            'password1': PASSWORD, 'password2': PASSWORD,
        }
        datos.update(extra)
        return datos

    def test_empleado_crea_cliente_con_empresa(self):
        self.entrar(self.empleado)
        r = self.client.post(reverse('gestion_crear_usuario'), self.datos_nueva('cliente'))
        self.assertRedirects(r, reverse('gestion_usuarios'))
        u = User.objects.get(username='nueva')
        self.assertEqual(roles.obtener_rol(u), roles.CLIENTE)
        self.assertEqual(u.perfil.empresa, self.empresa)
        reg = RegistroAuditoria.objects.get(accion='CREACION_CUENTA')
        self.assertEqual(reg.actor, self.empleado)

    def test_empleado_no_puede_crear_empleado_ni_admin(self):
        self.entrar(self.empleado)
        for rol in ['empleado', 'admin']:
            r = self.client.post(reverse('gestion_crear_usuario'), self.datos_nueva(rol))
            self.assertEqual(r.status_code, 200)
            self.assertFalse(User.objects.filter(username='nueva').exists())

    def test_admin_crea_otro_admin(self):
        self.entrar(self.admin)
        self.client.post(reverse('gestion_crear_usuario'), self.datos_nueva('admin'))
        u = User.objects.get(username='nueva')
        self.assertTrue(u.is_superuser and u.is_staff)
        self.assertIsNone(u.perfil.empresa)  # la empresa solo aplica a clientes

    def test_empleado_no_ve_ni_edita_otros_empleados(self):
        otro = crear_usuario('empleado2', roles.EMPLEADO)
        self.entrar(self.empleado)
        lista = self.client.get(reverse('gestion_usuarios'))
        self.assertContains(lista, 'cliente1')
        self.assertNotContains(lista, 'empleado2')
        self.assertNotContains(lista, 'admin1')
        self.assertEqual(self.client.get(reverse('gestion_editar_usuario', args=[otro.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse('gestion_editar_usuario', args=[self.admin.pk])).status_code, 403)

    def test_empleado_vincula_empresa_a_cliente_y_queda_auditado(self):
        self.entrar(self.empleado)
        r = self.client.post(reverse('gestion_editar_usuario', args=[self.cliente.pk]), {
            'first_name': 'Ana', 'last_name': '', 'email': 'cliente1@rodamar.cl', 'telefono': '',
            'rol': 'admin',  # intento de escalar: se ignora (campo deshabilitado)
            'empresa': self.empresa.pk,
        })
        self.assertEqual(r.status_code, 200)  # last_name es obligatorio
        r = self.client.post(reverse('gestion_editar_usuario', args=[self.cliente.pk]), {
            'first_name': 'Ana', 'last_name': 'Soto', 'email': 'cliente1@rodamar.cl', 'telefono': '',
            'rol': 'admin', 'empresa': self.empresa.pk,
        })
        self.assertRedirects(r, reverse('gestion_usuarios'))
        self.cliente.refresh_from_db()
        self.assertEqual(roles.obtener_rol(User.objects.get(pk=self.cliente.pk)), roles.CLIENTE)
        self.assertEqual(self.cliente.perfil.empresa, self.empresa)
        self.assertTrue(RegistroAuditoria.objects.filter(
            accion='EDICION_CUENTA', campo='Empresa cliente', actor=self.empleado).exists())

    def test_solo_admin_elimina_cuentas(self):
        self.entrar(self.empleado)
        self.assertEqual(self.client.post(reverse('gestion_eliminar_usuario', args=[self.cliente.pk])).status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.cliente.pk).exists())

        self.entrar(self.admin)
        r = self.client.post(reverse('gestion_eliminar_usuario', args=[self.cliente.pk]))
        self.assertRedirects(r, reverse('gestion_usuarios'))
        self.assertFalse(User.objects.filter(pk=self.cliente.pk).exists())
        reg = RegistroAuditoria.objects.get(accion='ELIMINACION_CUENTA')
        self.assertEqual(reg.usuario_afectado_texto, 'cliente1')  # se conserva aunque se borró
        self.assertIsNone(reg.usuario_afectado)

    def test_admin_no_se_elimina_a_si_mismo(self):
        self.entrar(self.admin)
        self.assertEqual(self.client.post(reverse('gestion_eliminar_usuario', args=[self.admin.pk])).status_code, 403)

    def test_admin_cambia_rol_y_queda_auditado(self):
        self.entrar(self.admin)
        self.client.post(reverse('gestion_editar_usuario', args=[self.cliente.pk]), {
            'first_name': 'Ana', 'last_name': 'Soto', 'email': 'cliente1@rodamar.cl', 'telefono': '',
            'rol': 'empleado', 'empresa': '', 'is_active': 'on',
        })
        self.assertEqual(roles.obtener_rol(User.objects.get(pk=self.cliente.pk)), roles.EMPLEADO)
        reg = RegistroAuditoria.objects.get(accion='CAMBIO_ROL')
        self.assertEqual((reg.valor_anterior, reg.valor_nuevo), ('Cliente', 'Empleado'))

    def test_admin_no_puede_quitarse_su_rol(self):
        self.entrar(self.admin)
        self.client.post(reverse('gestion_editar_usuario', args=[self.admin.pk]), {
            'first_name': 'Ad', 'last_name': 'Min', 'email': 'admin1@rodamar.cl', 'telefono': '', 'rol': 'cliente',
        })
        self.assertTrue(User.objects.get(pk=self.admin.pk).is_superuser)


# ---------------------------------------------------------------------------
# Mi perfil (auditado)
# ---------------------------------------------------------------------------
class MiPerfilTests(BaseRoles):
    def test_cliente_edita_sus_datos_y_queda_registro(self):
        self.entrar(self.cliente)
        r = self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana María', 'last_name': 'Rojas', 'email': 'ana@nuevo.cl', 'telefono': '+56 9 8765 4321',
            'password_actual': PASSWORD,
        })
        self.assertRedirects(r, reverse('mi_perfil'))
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.email, 'ana@nuevo.cl')
        self.assertEqual(self.cliente.perfil.telefono, '+56 9 8765 4321')

        registros = RegistroAuditoria.objects.filter(accion='EDICION_PERFIL', usuario_afectado=self.cliente)
        cambios = {r.campo: (r.valor_anterior, r.valor_nuevo) for r in registros}
        self.assertEqual(cambios['Correo'], ('cliente1@rodamar.cl', 'ana@nuevo.cl'))
        self.assertEqual(cambios['Nombre'], ('Ana', 'Ana María'))
        self.assertIn('Teléfono', cambios)
        self.assertTrue(all(r.actor == self.cliente for r in registros))

        # El historial se muestra en la página
        self.assertContains(self.client.get(reverse('mi_perfil')), 'ana@nuevo.cl')

    def test_cliente_no_puede_cambiar_empresa_ni_rol_desde_perfil(self):
        otra = Cliente.objects.create(nombre_completo='Otra', rut_o_id='77.222.222-K')
        self.entrar(self.cliente)
        self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': 'R', 'email': 'cliente1@rodamar.cl', 'telefono': '',
            'empresa': otra.pk, 'is_superuser': 'on', 'rol': 'admin',
        })
        u = User.objects.get(pk=self.cliente.pk)
        self.assertIsNone(u.perfil.empresa)
        self.assertEqual(roles.obtener_rol(u), roles.CLIENTE)

    def test_sin_cambios_no_genera_registros(self):
        self.entrar(self.cliente)
        self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': '', 'email': 'cliente1@rodamar.cl', 'telefono': '',
        })  # inválido (apellido obligatorio)
        self.cliente.last_name = 'R'
        self.cliente.save()
        self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': 'R', 'email': 'cliente1@rodamar.cl', 'telefono': '',
        })
        self.assertFalse(RegistroAuditoria.objects.filter(accion='EDICION_PERFIL').exists())

    def test_cambio_password_auditado(self):
        self.entrar(self.cliente)
        nueva = 'OtraClave#Puerto99'
        r = self.client.post(reverse('cambiar_password'), {
            'old_password': PASSWORD, 'new_password1': nueva, 'new_password2': nueva,
        })
        self.assertRedirects(r, reverse('mi_perfil'))
        self.assertTrue(RegistroAuditoria.objects.filter(accion='CAMBIO_PASSWORD', usuario_afectado=self.cliente).exists())


# ---------------------------------------------------------------------------
# Vista del cliente: solo vehículos de su empresa
# ---------------------------------------------------------------------------
class MisVehiculosTests(BaseRoles):
    def test_cliente_ve_solo_vehiculos_de_su_empresa(self):
        buque = Buque.objects.create(nombre='B', numero_viaje='1', fecha_atraque=date(2026, 10, 1))
        otra = Cliente.objects.create(nombre_completo='Otra', rut_o_id='77.222.222-K')
        Vehiculo.objects.create(chasis='PROPIO1', marca='M', modelo='X', buque=buque, cliente=self.empresa)
        Vehiculo.objects.create(chasis='AJENO1', marca='M', modelo='X', buque=buque, cliente=otra)
        self.cliente.perfil.empresa = self.empresa
        self.cliente.perfil.save()

        self.entrar(self.cliente)
        r = self.client.get(reverse('mis_vehiculos'))
        self.assertContains(r, 'PROPIO1')
        self.assertNotContains(r, 'AJENO1')

    def test_cliente_sin_empresa_ve_aviso(self):
        self.entrar(self.cliente)
        self.assertContains(self.client.get(reverse('mis_vehiculos')), 'todavía no está vinculada')

    def test_edicion_empresa_auditada(self):
        self.entrar(self.empleado)
        self.client.post(reverse('editar_empresa', args=[self.empresa.pk]), {
            'nombre_completo': 'Automotriz Norte SpA', 'rut_o_id': '76.111.111-6', 'telefono': '', 'email': '',
        })
        reg = RegistroAuditoria.objects.get(accion='EDICION_EMPRESA')
        self.assertEqual(reg.valor_nuevo, 'Automotriz Norte SpA')
        self.assertEqual(reg.actor, self.empleado)


# ---------------------------------------------------------------------------
# Bloqueo por intentos fallidos
# ---------------------------------------------------------------------------
@override_settings(LOGIN_MAX_INTENTOS_USUARIO=3, LOGIN_MAX_INTENTOS_IP=10, LOGIN_BLOQUEO_MINUTOS=15)
class BloqueoLoginTests(BaseRoles):
    def intentar(self, username='cliente1', password='mala', **extra):
        return self.client.post(reverse('login'), {'username': username, 'password': password}, **extra)

    def test_bloquea_tras_varios_fallos_incluso_con_clave_correcta(self):
        for _ in range(3):
            self.intentar()
        r = self.intentar(password=PASSWORD)
        self.assertContains(r, 'Demasiados intentos fallidos')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(RegistroAuditoria.objects.filter(accion='LOGIN_BLOQUEADO').exists())

    def test_login_correcto_reinicia_el_contador(self):
        for _ in range(2):
            self.intentar()
        self.assertRedirects(self.intentar(password=PASSWORD), reverse('mis_vehiculos'))
        self.client.logout()
        for _ in range(2):
            self.intentar()
        self.assertRedirects(self.intentar(password=PASSWORD), reverse('mis_vehiculos'))

    def test_bloqueo_por_correo_cuenta_para_el_mismo_usuario(self):
        for _ in range(3):
            self.intentar(username='cliente1@rodamar.cl')
        self.assertContains(self.intentar(password=PASSWORD), 'Demasiados intentos fallidos')

    def test_otro_usuario_no_queda_bloqueado(self):
        for _ in range(3):
            self.intentar()
        self.assertRedirects(self.intentar(username='empleado1', password=PASSWORD), reverse('dashboard'))

    def test_bloqueo_por_ip(self):
        for i in range(10):
            self.intentar(username=f'inventado{i}')
        self.assertContains(self.intentar(username='empleado1', password=PASSWORD), 'Demasiados intentos fallidos')
        # Desde otra IP sí puede entrar
        r = self.intentar(username='empleado1', password=PASSWORD, REMOTE_ADDR='10.0.0.99')
        self.assertRedirects(r, reverse('dashboard'))


# ---------------------------------------------------------------------------
# Recuperación de contraseña
# ---------------------------------------------------------------------------
class RecuperarPasswordTests(BaseRoles):
    def setUp(self):
        super().setUp()
        cache.clear()

    def pedir(self, email):
        return self.client.post(reverse('recuperar_password'), {'email': email})

    def enlace(self):
        cuerpo = mail.outbox[-1].body
        return next(l for l in cuerpo.splitlines() if '/usuarios/recuperar/' in l).strip()

    def test_flujo_completo(self):
        r = self.pedir('CLIENTE1@rodamar.cl')
        self.assertRedirects(r, reverse('recuperar_password_enviado'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['cliente1@rodamar.cl'])

        url = self.enlace().replace('http://testserver', '')
        r = self.client.get(url, follow=True)  # Django redirige a .../set-password/
        self.assertContains(r, 'Guardar contraseña')
        nueva = 'Recuperada#Puerto77'
        r = self.client.post(r.redirect_chain[-1][0], {'new_password1': nueva, 'new_password2': nueva})
        self.assertRedirects(r, reverse('recuperar_password_listo'))
        self.assertTrue(User.objects.get(pk=self.cliente.pk).check_password(nueva))
        self.assertTrue(RegistroAuditoria.objects.filter(accion='RESET_COMPLETADO', usuario_afectado=self.cliente).exists())

        # El enlace sirve una sola vez
        r = self.client.get(url, follow=True)
        self.assertContains(r, 'Este enlace no es válido')

    def test_correo_inexistente_misma_respuesta_y_sin_envio(self):
        r = self.pedir('nadie@nada.cl')
        self.assertRedirects(r, reverse('recuperar_password_enviado'))
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('no encontrada', RegistroAuditoria.objects.get(accion='RESET_SOLICITADO').detalle)

    def test_cuenta_inactiva_no_recibe_correo(self):
        self.cliente.is_active = False
        self.cliente.save()
        self.pedir('cliente1@rodamar.cl')
        self.assertEqual(len(mail.outbox), 0)

    def test_limite_de_solicitudes_por_correo(self):
        for _ in range(5):
            self.pedir('cliente1@rodamar.cl')
        self.assertEqual(len(mail.outbox), 3)  # RESET_MAX_POR_CORREO

    def test_token_manipulado_no_sirve(self):
        self.pedir('cliente1@rodamar.cl')
        url = self.enlace().replace('http://testserver', '')
        url_mala = url.rstrip('/')[:-3] + 'abc/'
        r = self.client.get(url_mala, follow=True)
        self.assertContains(r, 'Este enlace no es válido')

    def test_reset_desbloquea_el_login(self):
        with self.settings(LOGIN_MAX_INTENTOS_USUARIO=3):
            for _ in range(3):
                self.client.post(reverse('login'), {'username': 'cliente1', 'password': 'mala'})
            self.pedir('cliente1@rodamar.cl')
            r = self.client.get(self.enlace().replace('http://testserver', ''), follow=True)
            nueva = 'Recuperada#Puerto77'
            self.client.post(r.redirect_chain[-1][0], {'new_password1': nueva, 'new_password2': nueva})
            r = self.client.post(reverse('login'), {'username': 'cliente1', 'password': nueva})
            self.assertRedirects(r, reverse('mis_vehiculos'))

    def test_login_tiene_enlace_de_recuperacion(self):
        self.assertContains(self.client.get(reverse('login')), reverse('recuperar_password'))



class RevisionLogicaTests(BaseRoles):
    """Casos encontrados en la revisión del sistema."""

    def test_cambiar_correo_sin_contrasena_no_se_permite(self):
        self.entrar(self.cliente)
        r = self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': 'R', 'email': 'atacante@malo.cl', 'telefono': '',
        })
        self.assertContains(r, 'ingresa tu contraseña actual')
        self.assertEqual(User.objects.get(pk=self.cliente.pk).email, 'cliente1@rodamar.cl')
        r = self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': 'R', 'email': 'atacante@malo.cl', 'telefono': '', 'password_actual': 'mala',
        })
        self.assertEqual(User.objects.get(pk=self.cliente.pk).email, 'cliente1@rodamar.cl')

    def test_cambiar_nombre_no_pide_contrasena(self):
        self.entrar(self.cliente)
        r = self.client.post(reverse('mi_perfil'), {
            'first_name': 'Ana', 'last_name': 'Nueva', 'email': 'CLIENTE1@rodamar.cl', 'telefono': '',
        })
        self.assertRedirects(r, reverse('mi_perfil'))
        self.assertEqual(User.objects.get(pk=self.cliente.pk).last_name, 'Nueva')

    def test_enlace_admin_django_solo_para_rol_admin(self):
        staff = User.objects.create_user('staff1', 'staff1@x.cl', PASSWORD, is_staff=True)
        self.client.force_login(staff)
        self.assertNotContains(self.client.get(reverse('home')), 'Admin de Django')

    def test_admin_django_auditoria_carga(self):
        self.entrar(self.admin)
        self.assertEqual(self.client.get('/admin/usuarios/registroauditoria/').status_code, 200)
