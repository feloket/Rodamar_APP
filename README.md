# RODAMAR: Logística Portuaria y Muellaje Automotriz

Sistema web para controlar la descarga de buques, el manifiesto de vehículos, la ubicación en patio y el despacho en camiones cigüeña. Permite a las empresas cliente seguir sus vehículos y deja registro de cada operación.

Desarrollado con Django 5.2 LTS y MySQL para la asignatura Programación Back End (INACAP).

## Tabla de contenidos

- [Funcionalidades](#funcionalidades)
- [Roles y permisos](#roles-y-permisos)
- [Reglas de negocio](#reglas-de-negocio)
- [Instalación](#instalación)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Correo](#correo)
- [Respaldo y traslado de la base de datos](#respaldo-y-traslado-de-la-base-de-datos)
- [Pruebas](#pruebas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Seguridad](#seguridad)

## Funcionalidades

**Operación**

- CRUD de vehículos, buques, camiones cigüeña y empresas cliente desde el propio sitio, sin depender de Django Admin.
- Panel de operaciones con métricas y actualización rápida de estado y patio.
- Filtros por chasis, vehículo, color, buque, cliente, ubicación, cigüeña, estado y fecha.
- Historial de cada cambio de estado o de patio, con fecha y usuario.
- Validación de VIN (17 caracteres, sin I, O ni Q), RUT con dígito verificador y patente chilena. Los datos se guardan normalizados para evitar duplicados.

**Clientes**

- Rastreo público por chasis: cualquiera ve el estado y el patio. Los datos comerciales y el historial solo los ven la empresa dueña y el personal.
- Vista de los vehículos de la propia empresa.
- Registro público con confirmación de correo.

**Cuentas y auditoría**

- Gestión de cuentas y roles, exclusiva del administrador.
- Edición de los datos propios, con registro de cada cambio.
- Auditoría de accesos, cuentas y registros, con filtros por acción, rol, campo, IP, fecha y rango horario. Sus registros no se pueden editar ni borrar desde la aplicación.
- Recuperación de contraseña por correo.

**Interfaz**

- Modo día y noche, tamaño de texto ajustable y Bootstrap local: el sitio no necesita internet para verse bien.

## Roles y permisos

| Acción | Admin | Empleado | Cliente |
|---|:-:|:-:|:-:|
| Usar el panel y actualizar estados | Sí | Sí | No |
| Crear y editar vehículos, buques, camiones y empresas | Sí | Sí | No |
| Eliminar vehículos, buques, camiones y empresas | Sí | No | No |
| Ver, crear, editar y eliminar cuentas de otros usuarios | Sí | No | No |
| Vincular un cliente a su empresa | Sí | No | No |
| Retroceder o saltar estados de un vehículo | Sí | No | No |
| Ver la auditoría | Sí | No | No |
| Ver vehículos e historial | Todos | Todos | Solo de su empresa |
| Editar sus propios datos | Sí | Sí | Sí |

El registro público siempre crea cuentas de cliente. Los permisos se validan en el servidor (`usuarios/roles.py`): entrar por URL directa a una sección sin permiso devuelve un error 403.

## Reglas de negocio

**Flujo del vehículo:** `Descarga` → `Inspección` → `Traslado` → `Entregado`

- Un vehículo nuevo ingresa en el primer estado.
- Un empleado avanza de a un paso. Solo un administrador puede retroceder o saltar estados, para corregir errores, y el cambio queda en el historial.
- Traslado y Entregado exigen un camión cigüeña asignado.

**Integridad de los datos**

- No se puede eliminar un buque, una empresa o un camión que tenga vehículos asociados.
- No se pueden repetir el VIN, el RUT de una empresa, la patente, la combinación de buque y viaje, ni el correo de una cuenta.
- Un administrador no puede eliminarse, desactivarse ni cambiar su propio rol, así que el sistema siempre conserva al menos uno.

## Instalación

**Requisitos:** Python 3.10 o superior y MySQL 8.0 o superior.

### 1. Crear el entorno e instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate            # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Crear la base de datos y su usuario

Ejecuta lo siguiente en MySQL Workbench o con `mysql -u root -p`, usando una contraseña propia:

```sql
CREATE DATABASE rodamar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rodamar_user'@'localhost' IDENTIFIED BY 'tu_password_segura';
GRANT ALL PRIVILEGES ON rodamar_db.* TO 'rodamar_user'@'localhost';
-- Necesario para ejecutar las pruebas:
GRANT ALL PRIVILEGES ON test_rodamar_db.* TO 'rodamar_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configurar las variables de entorno

Crea el archivo `.env` con preguntas guiadas, o cópialo y edítalo a mano:

```bash
python scripts/configurar_env.py
# o bien: copy .env.example .env   (Linux/Mac: cp .env.example .env)
```

Las credenciales de conexión se cambian en estas variables del `.env`:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DB_NAME` | Nombre de la base | `rodamar_db` |
| `DB_USER` | Usuario de MySQL | `rodamar_user` |
| `DB_PASSWORD` | Contraseña, entre comillas simples | `'tu_password_segura'` |
| `DB_HOST` | Servidor | `localhost` |
| `DB_PORT` | Puerto | `3306` |

### 4. Crear las tablas y cargar los datos

Elige una de estas opciones:

```bash
# Opción A: aplicar las migraciones y generar los datos de muestra
python manage.py migrate
python manage.py datos_demo

# Opción B: importar el archivo SQL incluido y aplicar migraciones pendientes
python manage.py importar_sql database/rodamar_demo.sql
python manage.py migrate
```

### 5. Iniciar el servidor

```bash
python manage.py runserver
```

El sitio queda disponible en <http://127.0.0.1:8000>.

## Usuarios de prueba

Todos usan la contraseña `Rodamar#Demo2026`. Son cuentas y datos ficticios, exclusivos para evaluación.

| Usuario | Rol | Para comprobar |
|---|---|---|
| `admin_demo` | Administrador | Acceso total, gestión de cuentas y auditoría |
| `empleado_demo` | Empleado | Operación y CRUD, sin acceso a cuentas |
| `empleado2_demo` | Empleado | Lo mismo, con otro usuario |
| `cliente_demo` | Cliente de Automotriz del Norte SpA | Solo ve los vehículos de su empresa |
| `cliente_sur_demo` | Cliente de Comercial Sur Motors Ltda. | Separación de datos entre empresas |
| `cliente_sinempresa_demo` | Cliente sin empresa | Cuenta aún no vinculada |
| `cliente_pendiente_demo` | Cliente sin confirmar | Login rechazado hasta confirmar el correo |

Para probar el rastreo, usa el chasis `JTDKB20U093456781`: sin sesión se ven el estado y el patio, y con `cliente_demo` también el detalle y el historial.

Para crear un administrador propio: `python manage.py createsuperuser`.

## Correo

Por defecto, los correos de confirmación y de recuperación de contraseña **se imprimen en la terminal donde corre `runserver`**. Para evaluar el sistema basta con copiar el enlace desde ahí, sin configurar ninguna cuenta.

Para enviar correos reales, completa la sección SMTP del `.env` (ver `.env.example`) y comprueba la configuración:

```bash
python manage.py probar_correo tu.correo@ejemplo.cl
```

Si el envío falla, el comando indica la causa probable. Un administrador también puede marcar un correo como confirmado desde *Usuarios*.

## Respaldo y traslado de la base de datos

```bash
# Genera database/respaldo_FECHA.sql
python manage.py exportar_sql

# Carga un archivo en la base configurada en el .env
python manage.py importar_sql database/respaldo_FECHA.sql
python manage.py migrate
```

Ambos comandos leen las credenciales del `.env` y buscan `mysql` y `mysqldump` en el PATH y en las carpetas habituales de Windows.

> **Atención:** `importar_sql` reemplaza las tablas de la base de destino. Los respaldos pueden contener datos reales y están excluidos de git; solo se versiona `database/rodamar_demo.sql`.

## Pruebas

```bash
python manage.py test usuarios logistica
```

La suite cubre el CRUD y sus permisos, las validaciones, los roles, el registro y la confirmación de correo, el login y su bloqueo, la recuperación de contraseña, la auditoría, los filtros, la privacidad del rastreo y las reglas de negocio. Se ejecutó contra MySQL 8.0 con PyMySQL.

## Estructura del proyecto

```
django_project/    Configuración (settings, urls)
pages/             Página de inicio
logistica/         Buques, empresas, camiones, vehículos, historial y rastreo
  reglas.py        Flujo de estados del vehículo
  validadores.py   VIN, RUT, patente y teléfono
  views_crud.py    Listar, crear, editar y eliminar
  management/      Comando datos_demo
usuarios/          Login, registro, roles, perfil, cuentas y auditoría
  roles.py         Permisos por rol
  auditoria.py     Escritura de la bitácora
  correo.py        Enlace de confirmación de correo
  filtros.py       Filtros de fecha y orden de los listados
  seguridad.py     Bloqueo por intentos fallidos
  limites.py       Límite de peticiones
  signals.py       Perfil automático y auditoría de sesiones
  management/      Comandos exportar_sql, importar_sql, probar_correo y crear_grupos
database/          Datos de muestra listos para importar
scripts/           Creación guiada del .env
templates/         Plantillas HTML
static/            CSS, JavaScript, imágenes y Bootstrap 5.3 local
```

## Seguridad

- **Secretos:** la clave de Django y las credenciales se leen desde `.env`, que está excluido de git.
- **Formularios:** protección CSRF y validación en el servidor. Cerrar sesión solo se puede hacer por POST.
- **Contraseñas:** se usan los validadores de Django. Los enlaces de recuperación son de un solo uso y vencen en 1 hora.
- **Confirmación de correo:** el enlace va firmado y vence en 24 horas.
- **Fuerza bruta:** el login se bloquea 15 minutos tras 5 fallos por usuario o 30 por IP. Estos valores se configuran en `settings.py`.
- **Abuso de formularios:** el registro, el rastreo y los envíos de correo tienen límite de peticiones. Ese contador vive en la memoria del servidor y se reinicia con él.
- **Producción:** con `DEBUG=False`, las cookies solo viajan por HTTPS y se activan HSTS y la redirección a HTTPS.
