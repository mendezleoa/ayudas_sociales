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
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return conn

def create_table(conn):
    """Crea la tabla 'solicitudes' si no existe."""
    try:
        cursor = conn.cursor()
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
                detalles_miembros TEXT,
                descripcion_necesidad TEXT NOT NULL,
                tipo_ayuda TEXT NOT NULL,
                urgencia TEXT NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al crear la tabla: {e}")
