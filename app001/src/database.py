# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\database.py
import flet as ft
import re
import sqlite3

# --- Database Functions ---
DATABASE_FILE = "ayudas_sociales.db"

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        # Habilitar claves foráneas es buena práctica, aunque no las usemos activamente aún
        conn.execute("PRAGMA foreign_keys = ON")
        print("Conexión a base de datos establecida.") # Mensaje de confirmación
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return conn

def create_table(conn):
    """Crea las tablas necesarias si no existen."""
    if not conn:
        print("Error: No hay conexión a la base de datos para crear tablas.")
        return
    try:
        cursor = conn.cursor()
        print("Creando/Verificando tablas...")

        # --- Tabla Users (Existente) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """)
        # (Opcional: Código para insertar usuarios por defecto si no existen)
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("Insertando usuarios por defecto...")
            cursor.execute("""
                INSERT INTO users (username, password, role) VALUES
                ('operador1', 'pass1', 'operador'),
                ('admin1', 'adminpass', 'administrador')
            """)

        # --- Tabla Tipos de Ayuda (NUEVA) ---
        print("Creando/Verificando tabla 'tipos_ayuda'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipos_ayuda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT
            )
        """)
        # Insertar algunos tipos por defecto si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM tipos_ayuda")
        if cursor.fetchone()[0] == 0:
            print("Insertando tipos de ayuda por defecto...")
            cursor.execute("""
                INSERT INTO tipos_ayuda (nombre, descripcion) VALUES
                ('Alimentaria', 'Ayuda con alimentos básicos'),
                ('Económica', 'Apoyo monetario directo'),
                ('Vivienda', 'Ayuda para alquiler o reparaciones'),
                ('Salud', 'Asistencia médica o medicamentos')
            """)

        # --- Tabla Solicitudes (Existente) ---
        # Nota: Por ahora, mantenemos 'tipo_ayuda' como TEXT. Más adelante se podría
        #       cambiar a una clave foránea (tipo_ayuda_id INTEGER) si se desea
        #       mayor integridad referencial.
        print("Creando/Verificando tabla 'solicitudes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                identificacion TEXT NOT NULL,
                fecha_nacimiento TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT NOT NULL,
                ciudad TEXT NOT NULL,
                estado TEXT NOT NULL,
                codigo_postal TEXT NOT NULL,
                zona TEXT NOT NULL,
                num_miembros INTEGER,
                detalles_miembros TEXT, -- Considerar si aún es necesario
                descripcion_necesidad TEXT NOT NULL,
                tipo_ayuda TEXT NOT NULL, -- Mantenido como TEXT por ahora
                urgencia TEXT NOT NULL
            )
        """)

        # --- Tabla Miembros Familia (Existente) ---
        print("Creando/Verificando tabla 'miembros_familia'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS miembros_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solicitud_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                identificacion TEXT NOT NULL,
                relacion TEXT NOT NULL,
                fecha_nacimiento TEXT,
                condiciones_especiales TEXT,
                FOREIGN KEY (solicitud_id) REFERENCES solicitudes (id)
                ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Tablas verificadas/creadas correctamente.")
    except sqlite3.Error as e:
        print(f"Error al crear/verificar las tablas: {e}")
        conn.rollback() # Deshacer cambios si hubo error

# --- Funciones CRUD para Tipos de Ayuda ---

def add_aid_type(conn, nombre, descripcion):
    """
    Añade un nuevo tipo de ayuda a la tabla 'tipos_ayuda'.
    Devuelve el ID del nuevo registro o None si hay error.
    """
    sql = "INSERT INTO tipos_ayuda (nombre, descripcion) VALUES (?, ?)"
    if not conn:
        print("Error (add_aid_type): Sin conexión a DB.")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (nombre, descripcion))
        conn.commit()
        print(f"Tipo de ayuda '{nombre}' añadido con ID: {cursor.lastrowid}")
        return cursor.lastrowid
    except sqlite3.IntegrityError: # Manejar error de nombre duplicado (UNIQUE constraint)
        print(f"Error: El tipo de ayuda '{nombre}' ya existe.")
        return None # Indicar que no se pudo insertar
    except sqlite3.Error as e:
        print(f"Error al añadir tipo de ayuda: {e}")
        conn.rollback()
        return None

def get_all_aid_types(conn):
    """
    Obtiene todos los tipos de ayuda ordenados por nombre.
    Devuelve una lista de tuplas (id, nombre, descripcion) o una lista vacía si hay error.
    """
    if not conn:
        print("Error (get_all_aid_types): Sin conexión a DB.")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion FROM tipos_ayuda ORDER BY nombre")
        rows = cursor.fetchall()
        print(f"Obtenidos {len(rows)} tipos de ayuda.")
        return rows
    except sqlite3.Error as e:
        print(f"Error al obtener tipos de ayuda: {e}")
        return [] # Devolver lista vacía en caso de error

def update_aid_type(conn, aid_id, nombre, descripcion):
    """
    Actualiza un tipo de ayuda existente por su ID.
    Devuelve True si la actualización fue exitosa, False en caso contrario.
    """
    sql = "UPDATE tipos_ayuda SET nombre = ?, descripcion = ? WHERE id = ?"
    if not conn:
        print("Error (update_aid_type): Sin conexión a DB.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (nombre, descripcion, aid_id))
        conn.commit()
        # Verificar si alguna fila fue afectada
        if cursor.rowcount > 0:
            print(f"Tipo de ayuda ID {aid_id} actualizado a '{nombre}'.")
            return True
        else:
            print(f"Advertencia: No se encontró el tipo de ayuda con ID {aid_id} para actualizar.")
            return False # No se encontró el ID
    except sqlite3.IntegrityError:
        print(f"Error: Ya existe otro tipo de ayuda con el nombre '{nombre}'.")
        conn.rollback()
        return False
    except sqlite3.Error as e:
        print(f"Error al actualizar tipo de ayuda ID {aid_id}: {e}")
        conn.rollback()
        return False

def delete_aid_type(conn, aid_id):
    """
    Elimina un tipo de ayuda por su ID.
    Devuelve True si la eliminación fue exitosa, False en caso contrario.
    """
    # Opcional: Verificar si está en uso antes de borrar (más complejo si se usa como TEXT)
    # Si se usara FK (tipo_ayuda_id), se podría verificar más fácilmente.
    # Por ahora, permitimos borrar directamente.

    sql = "DELETE FROM tipos_ayuda WHERE id = ?"
    if not conn:
        print("Error (delete_aid_type): Sin conexión a DB.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (aid_id,))
        conn.commit()
        # Verificar si alguna fila fue afectada
        if cursor.rowcount > 0:
            print(f"Tipo de ayuda ID {aid_id} eliminado.")
            return True
        else:
            print(f"Advertencia: No se encontró el tipo de ayuda con ID {aid_id} para eliminar.")
            return False # No se encontró el ID
    except sqlite3.Error as e:
        # Podría fallar si hay restricciones de clave foránea en el futuro
        print(f"Error al eliminar tipo de ayuda ID {aid_id}: {e}")
        conn.rollback()
        return False

# --- Funciones existentes (Solicitudes, Miembros, etc.) ---
# (Mantener las funciones existentes como insert_family_member, get_all_requests, etc.)
# Asegúrate de que estas funciones también manejen la conexión y errores de forma similar.

def insert_family_member(conn, member_data):
    """Inserta un nuevo miembro familiar en la tabla miembros_familia."""
    sql = """
        INSERT INTO miembros_familia (
            solicitud_id, nombre, identificacion, relacion,
            fecha_nacimiento, condiciones_especiales
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, member_data)
        # No hacemos commit aquí, se hará al final de la transacción de la solicitud
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error al insertar miembro familiar: {e}")
        # No hacemos rollback aquí, se hará si falla la transacción principal
        return None

def get_all_requests(conn):
    """Obtiene todas las solicitudes."""
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, identificacion, fecha_nacimiento, telefono, email,
                   direccion, ciudad, estado, codigo_postal, zona,
                   num_miembros, detalles_miembros, descripcion_necesidad,
                   tipo_ayuda, urgencia
            FROM solicitudes
            ORDER BY id DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener las solicitudes: {e}")
        return []

def get_family_members(conn, solicitud_id):
    """Obtiene todos los miembros familiares de una solicitud."""
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM miembros_familia
            WHERE solicitud_id = ?
        """, (solicitud_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener miembros familiares: {e}")
        return []

# --- Bloque de prueba (Opcional) ---
if __name__ == "__main__":
    print("Probando funciones de database.py...")
    test_conn = create_connection()
    if test_conn:
        print("\n--- Probando create_table ---")
        create_table(test_conn)

        print("\n--- Probando add_aid_type ---")
        add_aid_type(test_conn, "Prueba Nueva", "Descripción de prueba")
        add_aid_type(test_conn, "Alimentaria", "Esto debería fallar (duplicado)") # Prueba de duplicado

        print("\n--- Probando get_all_aid_types ---")
        tipos = get_all_aid_types(test_conn)
        # for tipo in tipos:
        #     print(tipo)

        print("\n--- Probando update_aid_type ---")
        # Buscar ID de 'Prueba Nueva' para actualizar (asumiendo que se insertó)
        cursor = test_conn.cursor()
        cursor.execute("SELECT id FROM tipos_ayuda WHERE nombre = 'Prueba Nueva'")
        result = cursor.fetchone()
        if result:
            test_id = result[0]
            update_aid_type(test_conn, test_id, "Prueba Actualizada", "Descripción cambiada")
            update_aid_type(test_conn, test_id, "Económica", "Esto debería fallar (duplicado)") # Prueba duplicado en update
            update_aid_type(test_conn, 9999, "No Existe", "ID inválido") # Prueba ID no existente
        else:
            print("No se encontró 'Prueba Nueva' para actualizar.")


        print("\n--- Probando delete_aid_type ---")
        # Buscar ID de 'Prueba Actualizada' para eliminar
        cursor.execute("SELECT id FROM tipos_ayuda WHERE nombre = 'Prueba Actualizada'")
        result = cursor.fetchone()
        if result:
             test_id_del = result[0]
             delete_aid_type(test_conn, test_id_del)
             delete_aid_type(test_conn, test_id_del) # Intentar borrar de nuevo (debería fallar)
             delete_aid_type(test_conn, 9998, ) # ID no existente
        else:
            print("No se encontró 'Prueba Actualizada' para eliminar.")


        print("\n--- Lista final de tipos de ayuda ---")
        tipos_final = get_all_aid_types(test_conn)
        for tipo in tipos_final:
            print(tipo)

        test_conn.close()
        print("\nPruebas finalizadas. Conexión cerrada.")
    else:
        print("No se pudo establecer conexión para las pruebas.")

