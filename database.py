import sqlite3

def get_connection():
    conn = sqlite3.connect("araguaney_pos.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        nombre TEXT NOT NULL,
                        rol TEXT NOT NULL CHECK(rol IN ('ADMIN', 'CAJERO'))
                    )''')

    # Tabla de Productos (Incluye soporte para IVA e Imágenes)
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_barras TEXT UNIQUE NOT NULL,
                        descripcion TEXT NOT NULL,
                        precio_usd REAL NOT NULL,
                        stock INTEGER NOT NULL DEFAULT 0,
                        aplica_iva INTEGER NOT NULL DEFAULT 1,
                        imagen_path TEXT
                    )''')

    # Tabla de Proveedores
    cursor.execute('''CREATE TABLE IF NOT EXISTS proveedores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rif TEXT UNIQUE NOT NULL,
                        razon_social TEXT NOT NULL,
                        telefono TEXT NOT NULL,
                        direccion TEXT
                    )''')

    # Tabla de Ventas (Cabecera)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER NOT NULL,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        subtotal_usd REAL NOT NULL,
                        iva_usd REAL NOT NULL,
                        igtf_usd REAL NOT NULL,
                        total_usd REAL NOT NULL,
                        metodo_pago TEXT NOT NULL,
                        tasa_venda REAL NOT NULL,
                        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
                    )''')

    # Detalle de Ventas
    cursor.execute('''CREATE TABLE IF NOT EXISTS detalle_ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        venta_id INTEGER NOT NULL,
                        producto_id INTEGER NOT NULL,
                        cantidad INTEGER NOT NULL,
                        precio_unitario_usd REAL NOT NULL,
                        FOREIGN KEY(venta_id) REFERENCES ventas(id),
                        FOREIGN KEY(producto_id) REFERENCES productos(id)
                    )''')

    # Tabla de Configuración Fiscal (Fija para ID 1)
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracion (
                        id INTEGER PRIMARY KEY CHECK(id = 1),
                        nombre_comercio TEXT NOT NULL,
                        rif TEXT NOT NULL,
                        direccion TEXT NOT NULL,
                        iva_general REAL NOT NULL DEFAULT 16.0,
                        igtf REAL NOT NULL DEFAULT 3.0
                    )''')

    # Insertar valores iniciales por defecto si la base de datos está en blanco
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES ('admin', 'admin123', 'Administrador Principal', 'ADMIN')")
        cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES ('cajero', 'cajero123', 'Cajero de Turno', 'CAJERO')")

    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO configuracion (id, nombre_comercio, rif, direccion, iva_general, igtf) 
                          VALUES (1, 'ABASTO ARAGUANEY C.A.', 'J-12345678-9', 'AV. FUERZAS ARMADAS, CARACAS', 16.0, 3.0)''')

    conn.commit()
    conn.close()