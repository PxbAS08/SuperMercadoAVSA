USE avsaware_supermercado;

INSERT IGNORE INTO categorias (nombre, descripcion) VALUES
  ('Leche', 'Productos lacteos y leches saborizadas'),
  ('Yogurt', 'Yogurt natural, bebible y griego'),
  ('Mantequilla y Margarina', 'Untables lacteos y margarinas'),
  ('Snacks', 'Galletas, botanas y pastelitos'),
  ('Productos de Limpieza', 'Limpieza general, cloro, detergente y lavatrastes'),
  ('Bebidas', 'Refrescos, agua y jugos');

INSERT IGNORE INTO subcategorias (categoria_id, nombre) VALUES
  ((SELECT id FROM categorias WHERE nombre='Leche'), 'Entera'),
  ((SELECT id FROM categorias WHERE nombre='Leche'), 'Deslactosada'),
  ((SELECT id FROM categorias WHERE nombre='Leche'), 'Saborizada'),
  ((SELECT id FROM categorias WHERE nombre='Yogurt'), 'Bebible'),
  ((SELECT id FROM categorias WHERE nombre='Yogurt'), 'Natural'),
  ((SELECT id FROM categorias WHERE nombre='Yogurt'), 'Griego'),
  ((SELECT id FROM categorias WHERE nombre='Mantequilla y Margarina'), 'Mantequilla'),
  ((SELECT id FROM categorias WHERE nombre='Mantequilla y Margarina'), 'Margarina'),
  ((SELECT id FROM categorias WHERE nombre='Snacks'), 'Galletas'),
  ((SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas'),
  ((SELECT id FROM categorias WHERE nombre='Snacks'), 'Pastelitos'),
  ((SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Multiusos'),
  ((SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Cloro'),
  ((SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Detergentes'),
  ((SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Lavatrastes'),
  ((SELECT id FROM categorias WHERE nombre='Bebidas'), 'Refresco'),
  ((SELECT id FROM categorias WHERE nombre='Bebidas'), 'Agua'),
  ((SELECT id FROM categorias WHERE nombre='Bebidas'), 'Jugo');

INSERT IGNORE INTO usuarios
  (username, password_hash, nombre, email, telefono, rol_id, saldo_electronico)
VALUES
  ('admin', SHA2('admin123', 256), 'Administrador AVSAware',
   'admin@avsaware.local', '000-000-0000',
   (SELECT id FROM roles WHERE nombre='ADMIN'), 0.00),
  ('cliente', SHA2('cliente123', 256), 'Cliente de prueba',
   'cliente@avsaware.local', '000-000-0002',
   (SELECT id FROM roles WHERE nombre='CLIENTE'), 250.00);

INSERT IGNORE INTO productos
  (codigo, nombre, marca, categoria_id, subcategoria, presentacion,
   precio_venta, precio_compra)
VALUES
  ('L1', 'Lala Entera', 'Lala', (SELECT id FROM categorias WHERE nombre='Leche'), 'Entera', '1L', 28.50, 22.00),
  ('L2', 'Santa Clara Entera', 'Santa Clara', (SELECT id FROM categorias WHERE nombre='Leche'), 'Entera', '1L (6 piezas)', 230.00, 190.00),
  ('L3', 'Alpura Entera', 'Alpura', (SELECT id FROM categorias WHERE nombre='Leche'), 'Entera', '1L (6 piezas)', 180.00, 145.00),
  ('L4', 'Nutrileche Entera', 'Nutrileche', (SELECT id FROM categorias WHERE nombre='Leche'), 'Entera', '1L', 25.00, 19.00),
  ('L5', 'Lala Deslactosada', 'Lala', (SELECT id FROM categorias WHERE nombre='Leche'), 'Deslactosada', '1L (6 piezas)', 159.00, 126.00),
  ('L6', 'Alpura Deslactosada', 'Alpura', (SELECT id FROM categorias WHERE nombre='Leche'), 'Deslactosada', '1L', 30.00, 23.00),
  ('L8', 'Lala Yomi Vainilla', 'Lala', (SELECT id FROM categorias WHERE nombre='Leche'), 'Saborizada', '180ml', 10.00, 7.50),
  ('L9', 'Lala Yomi Chocolate', 'Lala', (SELECT id FROM categorias WHERE nombre='Leche'), 'Saborizada', '180ml', 10.00, 7.50),
  ('L10', 'Lala Yomi Fresa', 'Lala', (SELECT id FROM categorias WHERE nombre='Leche'), 'Saborizada', '180ml', 10.00, 7.50),
  ('Y1', 'Lala Fresa Bebible', 'Lala', (SELECT id FROM categorias WHERE nombre='Yogurt'), 'Bebible', '220g (8 piezas)', 70.00, 54.00),
  ('Y2', 'Alpura Natural', 'Alpura', (SELECT id FROM categorias WHERE nombre='Yogurt'), 'Natural', '1kg', 42.00, 32.00),
  ('Y3', 'Danone Griego', 'Danone', (SELECT id FROM categorias WHERE nombre='Yogurt'), 'Griego', '150g', 18.00, 13.00),
  ('M1', 'Lala sin sal', 'Lala', (SELECT id FROM categorias WHERE nombre='Mantequilla y Margarina'), 'Mantequilla', '90g', 24.00, 18.00),
  ('M2', 'Primavera', 'Primavera', (SELECT id FROM categorias WHERE nombre='Mantequilla y Margarina'), 'Margarina', '225g', 18.00, 13.00),
  ('S1', 'Marinela Canelitas', 'Marinela', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Galletas', '300g', 37.90, 28.00),
  ('S2', 'Chokiees', 'Gamesa', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Galletas', '300g', 107.00, 82.00),
  ('S3', 'Sponch', 'Marinela', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Galletas', '700g (4 paquetes)', 79.50, 58.00),
  ('S6A', 'Sabritas Clasicas', 'Sabritas', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas', '45g', 20.00, 14.00),
  ('S6B', 'Sabritas Flaming Hot', 'Sabritas', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas', '45g', 20.00, 14.00),
  ('S6C', 'Sabritas Adobadas', 'Sabritas', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas', '45g', 20.00, 14.00),
  ('S7', 'Doritos Nacho', 'Doritos', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas', '75g', 18.00, 13.00),
  ('S9A', 'Cheetos Torciditos', 'Cheetos', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Botanas', '80g', 15.00, 10.50),
  ('S11', 'Gansito Marinela', 'Marinela', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Pastelitos', '50g', 20.90, 15.00),
  ('S12', 'Pinguinos Marinela', 'Marinela', (SELECT id FROM categorias WHERE nombre='Snacks'), 'Pastelitos', '80g', 27.90, 20.00),
  ('PL1', 'Pinol El Original', 'Pinol', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Multiusos', '5.1L', 179.00, 132.00),
  ('PL2', 'Fabuloso', 'Fabuloso', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Multiusos', '6L', 199.00, 151.00),
  ('PL3', 'Cloralex', 'Cloralex', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Cloro', '1L', 68.00, 48.00),
  ('D1', 'Ariel Liquido Poder y Cuidado', 'Ariel', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Detergentes', '8.5L', 374.25, 290.00),
  ('D2', 'Persil en Polvo Ropa Color', 'Persil', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Detergentes', '9kg', 439.00, 330.00),
  ('LT1', 'Salvo Limon Liquido', 'Salvo', (SELECT id FROM categorias WHERE nombre='Productos de Limpieza'), 'Lavatrastes', '1.4L', 69.00, 48.00),
  ('B1', 'Coca-Cola lata', 'Coca-Cola', (SELECT id FROM categorias WHERE nombre='Bebidas'), 'Refresco', '355ml lata', 14.00, 10.00),
  ('B2', 'Coca-Cola botella', 'Coca-Cola', (SELECT id FROM categorias WHERE nombre='Bebidas'), 'Refresco', '600ml botella', 20.00, 15.00),
  ('B3', 'Pepsi', 'Pepsi', (SELECT id FROM categorias WHERE nombre='Bebidas'), 'Refresco', '2L botella', 32.00, 24.00),
  ('B4', 'Agua Bonafont', 'Bonafont', (SELECT id FROM categorias WHERE nombre='Bebidas'), 'Agua', '1.5L botella', 18.00, 12.00),
  ('B5', 'Jugo Del Valle Naranja', 'Del Valle', (SELECT id FROM categorias WHERE nombre='Bebidas'), 'Jugo', '1L tetrapack', 28.00, 20.00);

INSERT IGNORE INTO inventario
  (producto_id, stock_actual, stock_minimo, merma, ubicacion)
SELECT
  id,
  CASE
    WHEN codigo LIKE 'L%' THEN 58
    WHEN codigo LIKE 'S%' THEN 42
    WHEN codigo LIKE 'PL%' OR codigo LIKE 'D%' OR codigo LIKE 'LT%' THEN 24
    ELSE 36
  END,
  8,
  0,
  'Almacen principal'
FROM productos;

INSERT INTO compras (proveedor, usuario_id, total, notas)
SELECT 'Proveedor demo AVSAware', u.id, 3500.00,
       'Compra inicial de productos para pruebas'
FROM usuarios u
WHERE u.username = 'admin'
  AND NOT EXISTS (SELECT 1 FROM compras WHERE proveedor = 'Proveedor demo AVSAware');

INSERT INTO historial_operaciones
  (usuario_id, modulo, operacion, descripcion)
SELECT u.id, 'sistema', 'Datos iniciales',
       'Base de datos cargada con usuarios, productos, categorias e inventario de prueba'
FROM usuarios u
WHERE u.username = 'admin'
  AND NOT EXISTS (
    SELECT 1 FROM historial_operaciones
    WHERE modulo = 'sistema' AND operacion = 'Datos iniciales'
  );

INSERT INTO pedidos_cliente
  (cliente_id, modalidad_entrega_id, forma_pago_id, direccion_entrega,
   subtotal, total, estado)
SELECT u.id, me.id, fp.id, 'Recoger en tienda', 28.50, 28.50, 'PENDIENTE'
FROM usuarios u
JOIN modalidades_entrega me ON me.nombre = 'Recoger en tienda'
JOIN formas_pago fp ON fp.nombre = 'Dinero electronico'
WHERE u.username = 'cliente'
  AND NOT EXISTS (SELECT 1 FROM pedidos_cliente WHERE cliente_id = u.id);

INSERT INTO detalle_pedido
  (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
SELECT pc.id, p.id, 1, p.precio_venta, p.precio_venta
FROM pedidos_cliente pc
JOIN usuarios u ON u.id = pc.cliente_id
JOIN productos p ON p.codigo = 'L1'
WHERE u.username = 'cliente'
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido dp WHERE dp.pedido_id = pc.id
  );
