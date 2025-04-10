# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\solicitud.py
import flet as ft
import re
import sqlite3
from database import create_connection, create_table # Asumiendo que database.py está accesible

# --- Importar validadores ---
from validators import validate_required, validate_phone, validate_email, validate_numeric

# --- Database Functions ---
# DATABASE_FILE = "ayudas_sociales.db" # Ya definido en database.py

def insert_request(conn, request_data):
    """Inserta una nueva solicitud en la tabla 'solicitudes'."""
    sql = """
        INSERT INTO solicitudes (
            nombre, identificacion, fecha_nacimiento, telefono, email,
            direccion, ciudad, estado, codigo_postal, zona,
            num_miembros, detalles_miembros, descripcion_necesidad,
            tipo_ayuda, urgencia
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, request_data)
        conn.commit()
        return True # Indicar éxito
    except sqlite3.Error as e:
        print(f"Error al insertar la solicitud: {e}")
        return False # Indicar fallo

def get_all_requests(conn):
    """Obtiene todas las solicitudes de la tabla 'solicitudes'."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM solicitudes")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener las solicitudes: {e}")
        return []

# --- UI Building Functions ---

def build_personal_data_section():
    name_field = ft.TextField(label="Nombre Completo*", expand=True)
    id_field = ft.TextField(label="Número de Identificación*", expand=True)
    birth_date_field = ft.TextField(
        label="Fecha de Nacimiento",
        hint_text="DD/MM/AAAA",
        expand=True,
        # Considerar usar ft.DatePicker en el futuro
    )
    phone_field = ft.TextField(
        label="Número de Contacto*",
        expand=True,
        keyboard_type=ft.KeyboardType.PHONE,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"),
    )
    email_field = ft.TextField(
        label="Correo Electrónico",
        expand=True,
        keyboard_type=ft.KeyboardType.EMAIL
    )

    # Asociar validaciones on_change
    name_field.on_change = lambda e: validate_required(name_field, "Nombre")
    id_field.on_change = lambda e: validate_required(id_field, "Identificación")
    phone_field.on_change = lambda e: validate_phone(phone_field)
    email_field.on_change = lambda e: validate_email(email_field)

    return ft.Container(
        padding=ft.padding.all(15),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), # Opcional: fondo sutil
        border_radius=ft.border_radius.all(8),
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([name_field, id_field]),
                ft.Row([birth_date_field]),
                ft.Row([phone_field, email_field]),
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
        )
    ), name_field, id_field, birth_date_field, phone_field, email_field

def build_geographical_data_section():
    address_field = ft.TextField(label="Dirección Completa*", expand=True, multiline=True, max_lines=3)
    city_field = ft.TextField(label="Ciudad*", expand=1)
    state_field = ft.TextField(label="Estado/Provincia*", expand=1)
    postal_code_field = ft.TextField(
        label="Código Postal*",
        expand=1,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    zone_field = ft.TextField(label="Zona/Barrio/Sector*", expand=True)

    # Asociar validaciones
    address_field.on_change = lambda e: validate_required(address_field, "Dirección")
    city_field.on_change = lambda e: validate_required(city_field, "Ciudad")
    state_field.on_change = lambda e: validate_required(state_field, "Estado")
    postal_code_field.on_change = lambda e: validate_required(postal_code_field, "Código Postal")
    zone_field.on_change = lambda e: validate_required(zone_field, "Zona")

    return ft.Container(
        padding=ft.padding.all(15),
        border_radius=ft.border_radius.all(8),
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([address_field]),
                ft.Row([city_field, state_field, postal_code_field]),
                ft.Row([zone_field]),
            ],
        )
    ), address_field, city_field, state_field, postal_code_field, zone_field

def build_family_group_section():
    family_members_field = ft.TextField(
        label="Número de Miembros*",
        expand=1,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]")
    )
    family_details_field = ft.TextField(
        label="Detalles Relevantes del Grupo Familiar (Edades, condiciones especiales, etc.)",
        multiline=True,
        min_lines=3,
        max_lines=5,
        expand=True
    )

    # Asociar validaciones
    family_members_field.on_change = lambda e: validate_numeric(family_members_field, "Número de miembros")

    return ft.Container(
        padding=ft.padding.all(15),
        border_radius=ft.border_radius.all(8),
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([family_members_field]),
                ft.Row([family_details_field]),
            ],
        )
    ), family_members_field, family_details_field

def build_case_details_section():
    case_description_field = ft.TextField(
        label="Descripción Detallada de la Necesidad*",
        multiline=True,
        min_lines=3,
        max_lines=5,
        expand=True
    )
    # Opciones de ejemplo
    tipos_ayuda = ["Alimentos", "Vivienda", "Salud", "Educación", "Empleo", "Otro"]
    urgencias = ["Crítica (Inmediata)", "Alta (Próximos días)", "Media (Próximas semanas)", "Baja (Sin urgencia inmediata)"]

    aid_type_dropdown = ft.Dropdown(
        label="Tipo de Ayuda Solicitada*",
        options=[ft.dropdown.Option(tipo) for tipo in tipos_ayuda],
        expand=True,
    )
    urgency_dropdown = ft.Dropdown(
        label="Nivel de Urgencia*",
        options=[ft.dropdown.Option(urg) for urg in urgencias],
        expand=True,
    )

    # Asociar validaciones
    case_description_field.on_change = lambda e: validate_required(case_description_field, "Descripción")
    aid_type_dropdown.on_change = lambda e: validate_required(aid_type_dropdown, "Tipo de ayuda")
    urgency_dropdown.on_change = lambda e: validate_required(urgency_dropdown, "Urgencia")

    return ft.Container(
        padding=ft.padding.all(15),
        border_radius=ft.border_radius.all(8),
        expand=True,
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([case_description_field]),
                ft.Row([aid_type_dropdown, urgency_dropdown]),
            ],
        )
    ), case_description_field, aid_type_dropdown, urgency_dropdown

# --- Main Application ---
def main(page: ft.Page):
    page.title = "Registro de Solicitud de Ayudas Sociales"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = ft.padding.all(20)
    page.scroll = ft.ScrollMode.ADAPTIVE # Permitir scroll si el contenido excede

    # --- Database Connection ---
    conn = create_connection()
    if conn:
        create_table(conn)
    else:
        # Mostrar error si no se puede conectar
        page.add(ft.Text("Error crítico: No se pudo conectar a la base de datos.", color=ft.Colors.RED))
        return # Detener la ejecución si no hay DB

    # --- Build UI Sections ---
    personal_section_content, name_f, id_f, birth_f, phone_f, email_f = build_personal_data_section()
    geo_section_content, address_f, city_f, state_f, postal_f, zone_f = build_geographical_data_section()
    family_section_content, members_f, details_f = build_family_group_section()
    case_section_content, desc_f, aid_dd, urgency_dd = build_case_details_section()

    # --- Clear Form Function ---
    def clear_form():
        fields_to_clear = [
            name_f, id_f, birth_f, phone_f, email_f, address_f, city_f,
            state_f, postal_f, zone_f, members_f, details_f, desc_f
        ]
        dropdowns_to_clear = [aid_dd, urgency_dd]

        for field in fields_to_clear:
            field.value = ""
            field.error_text = None
        for dropdown in dropdowns_to_clear:
            dropdown.value = None
            dropdown.error_text = None
        page.update() # Actualizar todos los campos limpiados

    # --- Submit Form Logic ---
    def submit_form(e):
        # Validar todos los campos requeridos
        is_valid = True
        # Usamos '&=' para acumular resultados de validación
        is_valid &= validate_required(name_f, "Nombre")
        is_valid &= validate_required(id_f, "Identificación")
        is_valid &= validate_phone(phone_f)
        is_valid &= validate_email(email_f) # Email es opcional aquí, ajustar si es mandatorio
        is_valid &= validate_required(address_f, "Dirección")
        is_valid &= validate_required(city_f, "Ciudad")
        is_valid &= validate_required(state_f, "Estado")
        is_valid &= validate_required(postal_f, "Código Postal")
        is_valid &= validate_required(zone_f, "Zona")
        is_valid &= validate_numeric(members_f, "Número de miembros")
        is_valid &= validate_required(desc_f, "Descripción")
        is_valid &= validate_required(aid_dd, "Tipo de ayuda")
        is_valid &= validate_required(urgency_dd, "Urgencia")

        # No llames a page.update() aquí todavía, espera a mostrar el SnackBar si es necesario

        if is_valid:
            # Recopilar datos del formulario
            request_data = (
                name_f.value,
                id_f.value,
                birth_f.value, # Puede ser None si no se ingresa
                phone_f.value,
                email_f.value, # Puede ser None si no se ingresa
                address_f.value,
                city_f.value,
                state_f.value,
                postal_f.value,
                zone_f.value,
                int(members_f.value), # Convertir a entero
                details_f.value, # Puede ser None
                desc_f.value,
                aid_dd.value,
                urgency_dd.value,
            )

            # Insertar datos en la base de datos
            if conn:
                if insert_request(conn, request_data):
                    print("Datos guardados en la base de datos.")
                    # --- Correcto: Crear y mostrar SnackBar ---
                    success_snackbar = ft.SnackBar(
                        ft.Text("Solicitud guardada exitosamente."),
                        bgcolor=ft.Colors.GREEN_200
                    )
                    page.overlay.append(success_snackbar)
                    success_snackbar.open = True
                    # ------------------------------------------
                    clear_form() # Limpiar formulario después de guardar (esto ya llama a page.update())
                else:
                    # --- Correcto: Crear y mostrar SnackBar ---
                    db_error_snackbar = ft.SnackBar(
                        ft.Text("Error al guardar la solicitud en la base de datos."),
                        bgcolor=ft.Colors.RED_200
                    )
                    page.overlay.append(db_error_snackbar)
                    db_error_snackbar.open = True
                    page.update() # Actualizar para mostrar el SnackBar de error
                    # ------------------------------------------
            else:
                 # --- Correcto: Crear y mostrar SnackBar ---
                 conn_error_snackbar = ft.SnackBar(
                     ft.Text("Error: No hay conexión a la base de datos."),
                     bgcolor=ft.Colors.RED_200
                 )
                 page.overlay.append(conn_error_snackbar)
                 conn_error_snackbar.open = True
                 page.update() # Actualizar para mostrar el SnackBar de error
                 # ------------------------------------------

        else:
            print("Formulario inválido. Revise los campos marcados con *.")
            # --- Correcto: Crear y mostrar SnackBar ---
            validation_snackbar = ft.SnackBar(
                ft.Text("Formulario inválido. Por favor, revise los campos marcados con *."),
                bgcolor=ft.Colors.RED_400
            )
            page.overlay.append(validation_snackbar)
            validation_snackbar.open = True
            page.update() # Actualizar para mostrar mensajes de error Y el SnackBar
            # ------------------------------------------


    # --- Tabs ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True,
        tabs=[
            ft.Tab(
                text="Tab 1",
                content=ft.Column(
                    controls=[ft.Text("This is Tab 1")],
                ),
            ),
            ft.Tab(text="1. Datos Personales", content=personal_section_content),
            ft.Tab(text="2. Datos Geográficos", content=geo_section_content),
            ft.Tab(text="3. Grupo Familiar", content=family_section_content),
            ft.Tab(text="4. Detalles del Caso", content=case_section_content),
        ],
    )

    # --- Save Button ---
    save_button = ft.ElevatedButton(
        text="Guardar Solicitud",
        icon=ft.Icons.SAVE_ALT_OUTLINED,
        on_click=submit_form,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(vertical=12, horizontal=20)
        ),
        # width=250 # Opcional: Ancho fijo
    )

    # --- Main Layout ---
    page.add(
        ft.Column(
            expand=True, # Permitir que la columna principal se expanda
            controls=[
                ft.Text("Formulario de Registro de Solicitud", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Row(
                    [save_button],
                    alignment=ft.MainAxisAlignment.END # Alinear botón a la derecha
                ),
                tabs, # Las pestañas con su contenido
                ft.Divider(height=10, color="transparent"),
            ]
        )
    )

    # --- Database Cleanup ---
    def close_db_connection(e):
        print("Cerrando conexión a la base de datos...")
        if conn:
            conn.close()
            print("Conexión cerrada.")

    page.on_disconnect = close_db_connection

    page.update()

# --- Run App ---
if __name__ == "__main__":
    ft.app(target=main)
