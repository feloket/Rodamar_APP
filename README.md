# RODAMAR — Logística Portuaria y Muellaje Automotriz

Sistema web en **Django + MySQL** para controlar la descarga de buques, el manifiesto de vehículos, la ubicación en patio y el despacho en camiones cigüeña, con cuentas por rol y auditoría de seguridad.

## Funcionalidades

- **Rastreo público por chasis (VIN)**: el estado y el patio son públicos. Los datos comerciales (consignatario, RUT, buque, cigüeña) y el historial solo los ve la empresa dueña o el personal. Tiene límite de consultas por IP.
- **Panel operativo** para el personal: métricas, registro rápido desde modales y actualización de estado y patio.
- **CRUD completo** (menú *Registros*) de vehículos, buques, camiones cigüeña y empresas cliente: listados con búsqueda, filtros y paginación, además de crear, editar y eliminar. Eliminar es solo para el admin, y no se puede borrar un buque ni una empresa que tengan vehículos.
- **Validación de datos chilenos**: VIN (17 caracteres, sin I/O/Q), RUT con dígito verificador (módulo 11) y patente (BCDF-12 o AB-1234). Los datos se guardan normalizados, así que "76123456k" y "76.123.456-K" son el mismo RUT y no se duplican.
- **Historial de estados**: cada cambio de estado o de patio queda registrado con fecha y usuario (también los que se hacen desde `/admin/`).
- **Cuentas por rol**: Admin, Empleado y Cliente (detalle abajo).
- **Mis datos**: cada usuario edita su nombre, correo y teléfono. Cada cambio queda auditado con el valor anterior y el nuevo.
- **Auditoría de seguridad** (solo admin): logins (incluidos los fallidos y bloqueados), logout, registros, creación y eliminación de cuentas, cambios de rol, de contraseña y de empresas. Los registros no se pueden editar ni borrar.
- **Seguridad del login**: "Recordarme", bloqueo tras varios intentos fallidos, logout solo por POST y recuperación de contraseña por correo con token de un solo uso que vence en 1 hora.
- **Modo día / noche** y **accesibilidad** (tamaño de texto de 87,5 % a 150 %, atajos Alt + / Alt − / Alt 0).

## Roles

| Acción | Admin | Empleado | Cliente |
|---|:-:|:-:|:-:|
| Panel operativo (buques, vehículos, estados) | ✅ | ✅ | ❌ |
| Crear / editar empresas, buques, camiones y vehículos | ✅ | ✅ | ❌ |
| Eliminar empresas, buques, camiones y vehículos | ✅ | ❌ | ❌ |
| Crear cuentas | todos los roles | solo clientes | ❌ |
| Vincular un cliente a su empresa | ✅ | ✅ | ❌ |
| Eliminar cuentas, cambiar roles, desactivar | ✅ | ❌ | ❌ |
| Ver auditoría | ✅ | ❌ | ❌ |
| Ver vehículos de su empresa + historial | ✅ | ✅ | ✅ (solo los suyos) |
| Editar sus propios datos | ✅ | ✅ | ✅ |

- El **registro público** siempre crea cuentas de **cliente**. Las de empleado y admin las crea un admin desde *Usuarios*.
- Los permisos se validan en el servidor (`usuarios/roles.py`), no solo en el navbar: entrar por URL directa a una sección sin permiso devuelve **403**.

## Instalación

Requisitos: Python 3.12+ y MySQL 8.

```bash
# 1. Entorno virtual y dependencias
python -m venv venv
venv\Scripts\activate            # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

# 2. Variables de entorno
copy .env.example .env           # Linux/Mac: cp .env.example .env
#    -> edita .env (SECRET_KEY, datos de MySQL)
```

Crea la base de datos y el usuario en MySQL:

```sql
CREATE DATABASE rodamar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rodamar_user'@'localhost' IDENTIFIED BY 'tu_password_segura';
GRANT ALL PRIVILEGES ON rodamar_db.* TO 'rodamar_user'@'localhost';
-- Para poder correr los tests (Django crea una base temporal test_rodamar_db):
GRANT ALL PRIVILEGES ON test_rodamar_db.* TO 'rodamar_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# 3. Tablas, grupos de roles y datos de prueba
python manage.py migrate
python manage.py datos_demo        # opcional, solo con DEBUG=True

# 4. Levantar el servidor
python manage.py runserver
```

### Cuentas de demostración (`datos_demo`)

| Usuario | Rol | Contraseña |
|---|---|---|
| `admin_demo` | Administrador | `Rodamar#Demo2026` |
| `empleado_demo` | Empleado | `Rodamar#Demo2026` |
| `cliente_demo` | Cliente (Automotriz del Norte SpA) | `Rodamar#Demo2026` |

Prueba el rastreo con el chasis `JTDKB20U093456781`: sin sesión verás solo el estado, y con `cliente_demo` verás también el historial.

Para crear tu propio admin: `python manage.py createsuperuser`.

## Recuperación de contraseña sin servidor de correo

El proyecto usa el backend de correo de **consola** (`EMAIL_BACKEND` en `.env`). Al pedir "¿Olvidaste tu contraseña?", el correo con el enlace **se imprime en la terminal donde corre `runserver`** y no sale del computador. Copia el enlace desde ahí.

Para enviar correos reales basta con cambiar `EMAIL_BACKEND` a SMTP y configurar `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD`. El código no cambia.

## Tests

```bash
python manage.py test usuarios logistica
```

Probado contra SQLite y MariaDB 10.11 (compatible con MySQL), con PyMySQL. El sistema no necesita las tablas de zona horaria de MySQL, que en Windows normalmente no vienen instaladas.

Cubren el CRUD y sus permisos, las validaciones de VIN, RUT y patente, los permisos por rol, registro, login, logout, bloqueo por fuerza bruta, recuperación de contraseña, auditoría, privacidad del rastreo, historial de estados y protección contra borrado en cascada.

## Estructura

```
django_project/   configuración (settings, urls)
pages/            página de inicio
logistica/        buques, empresas, camiones, vehículos, historial, rastreo
  management/commands/datos_demo.py
usuarios/         login, registro, roles, perfil, gestión de cuentas, auditoría
  roles.py        quién puede hacer qué (decorador @rol_requerido)
  auditoria.py    escritura de la bitácora
  seguridad.py    bloqueo por intentos fallidos
  limites.py      límite de peticiones (rastreo, recuperación de contraseña)
  signals.py      perfil automático y auditoría de login/logout
logistica/
  views_crud.py   listar / crear / editar / eliminar (buques, camiones, vehículos, empresas)
  validadores.py  VIN, RUT (módulo 11) y patente chilena
templates/        HTML (Bootstrap 5.3)
static/           css/rodamar.css, js/preferencias.js (tema y tamaño de texto), img
  vendor/bootstrap-5.3.3/   Bootstrap local: la app funciona sin internet
```

## Notas de seguridad

- Las contraseñas usan los validadores de Django (largo, similitud, comunes, numéricas).
- El bloqueo de login actúa tras 5 fallos por usuario o 30 por IP, durante 15 minutos (configurable en `settings.py`).
- Con `DEBUG=False`, las cookies solo viajan por HTTPS y se activa HSTS y la redirección a HTTPS.
- La caché que usan los límites de peticiones vive en memoria y se reinicia al reiniciar el servidor. Para un proyecto local basta; en producción se usaría Redis.
