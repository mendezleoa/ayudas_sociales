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
    """Crea las tablas necesarias si no existen."""
    try:
        cursor = conn.cursor()
        # Tabla principal de solicitudes
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
        
        # Nueva tabla para miembros familiares
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
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")

def insert_family_member(conn,member_data):
    """Inserta un nuevo miembro familiar en la tabla miembros_familia."""
    sql = """
        INSERT INTO miembros_familia (
            solicitud_id, nombre, identificacion, relacion,
            fecha_nacimiento, condiciones_especiales
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, member_data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error al insertar miembro familiar: {e}")
        return None
    
def get_family_members(conn, solicitud_id):
    """Obtiene todos los miembros familiares de una solicitud."""
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
    

def build_family_group_section():
    family_members_field = ft.TextField(
        label="Número de Miembros*",
        expand=1,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]")
    )
    
    # Campos para cada miembro familiar
    member_fields = []
    
    def add_member_fields():
        member_container = ft.Container(
            content=ft.Column([
                ft.TextField(label="Nombre Completo*", expand=True),
                ft.TextField(label="Identificación*", expand=True),
                ft.TextField(label="Relación/Parentesco*", expand=True),
                ft.TextField(
                    label="Fecha de Nacimiento",
                    hint_text="DD/MM/AAAA",
                    expand=True
                ),
                ft.TextField(
                    label="Condiciones Especiales",
                    multiline=True,
                    min_lines=2,
                    max_lines=3,
                    expand=True
                ),
                ft.Divider(height=10, color="transparent"),
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=8,
            margin=ft.margin.only(bottom=10)
        )
        member_fields.append(member_container)
        return member_container
    
    def update_member_fields(e):
        try:
            num_members = int(family_members_field.value or 0)
            current_members = len(member_fields)
            
            if num_members > current_members:
                # Agregar campos adicionales
                for _ in range(num_members - current_members):
                    members_column.controls.append(add_member_fields())
            elif num_members < current_members:
                # Remover campos excedentes
                for _ in range(current_members - num_members):
                    member_fields.pop()
                    members_column.controls.pop()
            
            #page.update()
        except ValueError:
            pass
    family_members_field.on_change = update_member_fields
    
    members_column = ft.Column(
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
    return ft.Container(
        padding=ft.padding.all(15),
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([family_members_field]),
                members_column,
            ],
        )
    ), family_members_field, member_fields