# AVSAware - Sistema de Gestion para Supermercado

AVSAware es una aplicacion de escritorio en Python orientada a la administracion interna y atencion en linea de un supermercado pequeno o mediano. El nucleo del sistema cubre login, productos, categorias, inventario, usuarios, pedidos de cliente, historial, devoluciones, cancelaciones y reportes basicos.

El modulo de cliente tambien esta incluido, pero se presenta como funcion complementaria: se usa solo si el negocio requiere seleccion de productos, carrito, saldo electronico, recoger en tienda o entrega a domicilio.

## Tecnologias

- Python 3.10 o superior.
- Tkinter para la interfaz de escritorio.
- MySQL Server como base de datos principal.
- MySQL Workbench para administrar/importar la base.
- `mysql-connector-python` para conectar Python con MySQL.
- PyInstaller para generar ejecutable.
- Logo corporativo AVSAware en `assets/logo.png`.

## Estructura

```text
main.py
requirements.txt
README.md
config/
  db_config.py
database/
  avsaware_schema.sql
  seed_data.sql
models/
controllers/
views/
assets/
utils/
data/comprobantes/
```

## Requisitos previos

1. Instalar Python.
2. Instalar MySQL Server.
3. Instalar MySQL Workbench.
4. Tener un usuario MySQL local con permisos para crear bases de datos.

## Instalacion

Desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Crear la base de datos en MySQL Workbench

1. Abrir MySQL Workbench.
2. Conectarse a la instancia local.
3. Abrir `database/avsaware_schema.sql`.
4. Ejecutar todo el script.
5. Abrir `database/seed_data.sql`.
6. Ejecutar todo el script.
7. Confirmar que exista la base `avsaware_supermercado`.

Si ya habias importado la base antes de agregar el modulo de subcategorias, vuelve a ejecutar `avsaware_schema.sql` y despues `seed_data.sql`. Los scripts usan `CREATE TABLE IF NOT EXISTS` e `INSERT IGNORE`, por lo que agregan lo nuevo sin duplicar registros base.

Tablas principales incluidas:

- `usuarios`
- `roles`
- `productos`
- `categorias`
- `subcategorias`
- `inventario`
- `ventas`
- `detalle_venta`
- `compras`
- `devoluciones`
- `cancelaciones`
- `comprobantes`
- `historial_operaciones`
- `pedidos_cliente`
- `detalle_pedido`
- `modalidades_entrega`
- `formas_pago`

## Configuracion de conexion

La conexion esta centralizada en `config/db_config.py`. Por defecto usa:

```text
host: 127.0.0.1
usuario: root
password: vacio
base: avsaware_supermercado
puerto: 3306
```

Tambien puedes configurar sin tocar el codigo mediante variables de entorno:

```powershell
$env:AVSAWARE_DB_HOST="127.0.0.1"
$env:AVSAWARE_DB_USER="root"
$env:AVSAWARE_DB_PASSWORD="tu_password"
$env:AVSAWARE_DB_NAME="avsaware_supermercado"
$env:AVSAWARE_DB_PORT="3306"
```

## Ejecutar el sistema

```powershell
python main.py
```

Si MySQL no esta instalado, el servidor no esta activo o la base no fue importada, el sistema mostrara un error de conexion.

## Usuarios de prueba

| Rol | Usuario | Contrasena |
| --- | --- | --- |
| Administrador | `admin` | `admin123` |
| Cliente | `cliente` | `cliente123` |

## Roles y permisos

Administrador:

- Acceso completo a panel, usuarios, productos, categorias, subcategorias, inventario, pedidos, devoluciones, historial, reportes y configuracion.
- Puede dar de alta y editar productos, usuarios, categorias y subcategorias.
- Puede consultar datos publicos de clientes, como nombre, correo, telefono y direccion.
- Puede desactivar usuarios con confirmacion, evitando eliminar el ultimo administrador activo.
- Ve graficas administrativas en el panel principal.

Cliente:

- Modulo complementario con compras, carrito, saldo electronico, perfil, tarjetas guardadas y pedidos propios.
- No tiene acceso al panel administrativo ni a informacion interna.
- Puede editar sus datos personales y gestionar sus tarjetas guardadas. Los datos bancarios privados no se muestran al administrador.

## Modulos administrativos

- Login y control de roles.
- Panel de administrador con metricas operativas.
- Grafica de pedidos por dia para administrador.
- Gestion de productos y categorias.
- Gestion de subcategorias dependientes de categoria.
- Control de inventario con ajustes manuales.
- Historial de operaciones.
- Cambio de estado de pedidos: en proceso, listo para entrega, entregado, cancelado o devuelto.
- Administracion de usuarios con datos de contacto y desactivacion segura.
- Reporte de stock bajo y pedidos del dia.
- Consulta y seguimiento de pedidos de cliente.

## Modulos de cliente opcionales

- Inicio del cliente.
- Seleccion de productos.
- Carrito del cliente.
- Consulta de saldo electronico.
- Consulta de pedidos propios.
- Perfil editable: nombre, correo, telefono y direccion.
- Gestion de tarjetas guardadas sin exponer datos bancarios completos.
- Modalidad de compra: recoger en tienda o entrega a domicilio.
- Formas de pago: efectivo, dinero electronico o tarjeta.
- Pasarela de pago para tarjeta con numero, titular, vencimiento, CVV y opcion de guardar tarjeta.
- Registro de pedidos del cliente.

Estos modulos no sustituyen el enfoque administrativo. Solo amplian el sistema si el negocio desea atencion directa a clientes.

## Generar ejecutable con PyInstaller

Primero verifica que la app ejecute correctamente con `python main.py`. Luego:

```powershell
pyinstaller --onefile --windowed --name AVSAware --add-data "assets;assets" --add-data "data;data" main.py
```

El ejecutable se generara en `dist/AVSAware.exe`.

Notas importantes:

- MySQL debe estar instalado antes de abrir el ejecutable.
- La base `avsaware_supermercado` debe estar creada e importada.
- Las variables de entorno de conexion siguen aplicando al ejecutable.
- Si agregas nuevos iconos o archivos externos, colocalos en `assets/` o `data/` y agregalos al comando `--add-data`.

## Alcance y restricciones cubiertas

- No se usa SQLite como base principal.
- La conexion MySQL esta centralizada.
- El proyecto no esta en un solo archivo.
- La estructura esta preparada para PyInstaller.
- Los modulos de cliente existen como complementarios.
- El diseno conserva la identidad visual AVSAware: verde, blanco, flujo simple y enfoque operativo.
