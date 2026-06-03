CREATE DATABASE IF NOT EXISTS avsaware_supermercado
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE avsaware_supermercado;

CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(40) NOT NULL UNIQUE,
  descripcion VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(60) NOT NULL UNIQUE,
  password_hash CHAR(64) NOT NULL,
  nombre VARCHAR(120) NOT NULL,
  email VARCHAR(120) NULL,
  telefono VARCHAR(40) NULL,
  direccion VARCHAR(255) NULL,
  rol_id INT NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  saldo_electronico DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_roles
    FOREIGN KEY (rol_id) REFERENCES roles(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE,
  descripcion VARCHAR(255) NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subcategorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  categoria_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  activa TINYINT(1) NOT NULL DEFAULT 1,
  CONSTRAINT uq_subcategorias_categoria_nombre
    UNIQUE (categoria_id, nombre),
  CONSTRAINT fk_subcategorias_categorias
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(30) NOT NULL UNIQUE,
  nombre VARCHAR(160) NOT NULL,
  marca VARCHAR(100) NOT NULL,
  categoria_id INT NOT NULL,
  subcategoria VARCHAR(100) NULL,
  presentacion VARCHAR(80) NULL,
  precio_venta DECIMAL(10,2) NOT NULL,
  precio_compra DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_productos_categorias
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventario (
  producto_id INT PRIMARY KEY,
  stock_actual INT NOT NULL DEFAULT 0,
  stock_minimo INT NOT NULL DEFAULT 5,
  merma INT NOT NULL DEFAULT 0,
  ubicacion VARCHAR(80) NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inventario_productos
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS formas_pago (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(60) NOT NULL UNIQUE,
  activa TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS modalidades_entrega (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE,
  activa TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  folio VARCHAR(40) NOT NULL UNIQUE,
  usuario_id INT NOT NULL,
  cliente_id INT NULL,
  forma_pago_id INT NOT NULL,
  modalidad_entrega_id INT NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  descuento DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  total DECIMAL(10,2) NOT NULL,
  monto_efectivo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  monto_saldo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  estado VARCHAR(30) NOT NULL DEFAULT 'COMPLETADA',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ventas_usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
  CONSTRAINT fk_ventas_clientes
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
  CONSTRAINT fk_ventas_formas_pago
    FOREIGN KEY (forma_pago_id) REFERENCES formas_pago(id),
  CONSTRAINT fk_ventas_modalidades
    FOREIGN KEY (modalidad_entrega_id) REFERENCES modalidades_entrega(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_venta (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  producto_id INT NOT NULL,
  cantidad INT NOT NULL,
  cantidad_devuelta INT NOT NULL DEFAULT 0,
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_detalle_venta_ventas
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
  CONSTRAINT fk_detalle_venta_productos
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS compras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  proveedor VARCHAR(120) NOT NULL,
  usuario_id INT NOT NULL,
  fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  notas TEXT NULL,
  CONSTRAINT fk_compras_usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS devoluciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  detalle_venta_id INT NULL,
  usuario_id INT NOT NULL,
  motivo VARCHAR(120) NOT NULL,
  monto DECIMAL(10,2) NOT NULL,
  tipo_reembolso VARCHAR(60) NOT NULL,
  estado VARCHAR(30) NOT NULL DEFAULT 'APLICADA',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_devoluciones_ventas
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
  CONSTRAINT fk_devoluciones_detalle
    FOREIGN KEY (detalle_venta_id) REFERENCES detalle_venta(id),
  CONSTRAINT fk_devoluciones_usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cancelaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  usuario_id INT NOT NULL,
  motivo VARCHAR(160) NOT NULL,
  monto DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cancelaciones_ventas
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
  CONSTRAINT fk_cancelaciones_usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS comprobantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  folio VARCHAR(40) NOT NULL,
  tipo VARCHAR(40) NOT NULL,
  ruta_archivo VARCHAR(255) NULL,
  contenido TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_comprobantes_ventas
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS historial_operaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NULL,
  modulo VARCHAR(80) NOT NULL,
  operacion VARCHAR(100) NOT NULL,
  descripcion TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_historial_usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedidos_cliente (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT NOT NULL,
  modalidad_entrega_id INT NOT NULL,
  forma_pago_id INT NOT NULL,
  direccion_entrega VARCHAR(255) NULL,
  estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
  subtotal DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_pedidos_cliente
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
  CONSTRAINT fk_pedidos_modalidades
    FOREIGN KEY (modalidad_entrega_id) REFERENCES modalidades_entrega(id),
  CONSTRAINT fk_pedidos_formas_pago
    FOREIGN KEY (forma_pago_id) REFERENCES formas_pago(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_pedido (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT NOT NULL,
  producto_id INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_detalle_pedido_pedidos
    FOREIGN KEY (pedido_id) REFERENCES pedidos_cliente(id),
  CONSTRAINT fk_detalle_pedido_productos
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tarjetas_cliente (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT NOT NULL,
  alias VARCHAR(80) NOT NULL,
  titular VARCHAR(120) NOT NULL,
  marca VARCHAR(40) NOT NULL,
  ultimos4 CHAR(4) NOT NULL,
  vencimiento VARCHAR(7) NOT NULL,
  favorita TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_tarjetas_cliente_usuario
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (nombre, descripcion) VALUES
  ('ADMIN', 'Acceso completo al panel administrativo'),
  ('CLIENTE', 'Modulo complementario para pedidos de cliente');

INSERT IGNORE INTO formas_pago (nombre) VALUES
  ('Efectivo'),
  ('Dinero electronico'),
  ('Tarjeta');

INSERT IGNORE INTO modalidades_entrega (nombre) VALUES
  ('Compra en tienda'),
  ('Recoger en tienda'),
  ('Entrega a domicilio');
