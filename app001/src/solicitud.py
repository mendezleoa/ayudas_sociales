import flet as ft
import re
import sqlite3
from database import create_connection,create_table

# --- Database Functions ---
DATABASE_FILE = "ayudas_sociales.db"

def insert_request(conn, request_data):
    """Inserta una nueva solicitud en la tabla 'solicitudes'."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitudes (
                nombre, identificacion, fecha_nacimiento, telefono, email,
                direccion, ciudad, estado, codigo_postal, zona,
                num_miembros, detalles_miembros, descripcion_necesidad,
                tipo_ayuda, urgencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, request_data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al insertar la solicitud: {e}")

def get_all_requests(conn):
    """Obtiene todas las solicitudes de la tabla 'solicitudes'."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM solicitudes")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener las solicitudes: {e}")
        return []

# --- Flet App ---
def main(page: ft.Page):
    page.title = "Registro de Ayudas Sociales"
    page.vertical_alignment = ft.MainAxisAlignment.START

    # --- Conexión a la Base de Datos ---
    conn = create_connection()
    if conn:
        create_table(conn)

    # --- Funciones de Validación ---
    def validate_name(control):
        """Valida que el nombre no esté vacío."""
        if not control.value:
            control.error_text = "El nombre es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_id(control):
        """Valida que el ID no esté vacío."""
        if not control.value:
            control.error_text = "El ID es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_phone(control):
        """Valida que el teléfono tenga un formato correcto."""
        phone_pattern = r"^\d{10}$"  # Ejemplo: 10 dígitos
        if not re.match(phone_pattern, control.value):
            control.error_text = "Formato de teléfono incorrecto (10 dígitos)"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_email(control):
        """Valida que el correo electrónico tenga un formato correcto."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, control.value):
            control.error_text = "Formato de correo electrónico incorrecto"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_address(control):
        """Valida que la dirección no esté vacía."""
        if not control.value:
            control.error_text = "La dirección es requerida"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_city(control):
        """Valida que la ciudad no esté vacía."""
        if not control.value:
            control.error_text = "La ciudad es requerida"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_state(control):
        """Valida que el estado no esté vacío."""
        if not control.value:
            control.error_text = "El estado es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_postal_code(control):
        """Valida que el código postal no esté vacío."""
        if not control.value:
            control.error_text = "El código postal es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True
    
    def validate_zone(control):
        """Valida que la zona no esté vacía."""
        if not control.value:
            control.error_text = "La zona es requerida"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_family_members(control):
        """Valida que el número de miembros no esté vacío."""
        if not control.value:
            control.error_text = "El número de miembros es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_case_description(control):
        """Valida que la descripción del caso no esté vacía."""
        if not control.value:
            control.error_text = "La descripción del caso es requerida"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_aid_type(control):
        """Valida que el tipo de ayuda no esté vacío."""
        if not control.value:
            control.error_text = "El tipo de ayuda es requerido"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    def validate_urgency(control):
        """Valida que la urgencia no esté vacía."""
        if not control.value:
            control.error_text = "La urgencia es requerida"
            page.update()
            return False
        control.error_text = None
        page.update()
        return True

    # --- Sección de Datos Personales ---
    personal_data_section = ft.Column(
        controls=[
            name_field := ft.TextField(label="Nombre Completo", expand=True, on_change=lambda e: validate_name(name_field)),
            id_field := ft.TextField(label="Número de Identificación", expand=True, on_change=lambda e: validate_id(id_field)),
            birth_date_field := ft.TextField(label="Fecha de Nacimiento", expand=True),  # Considerar DatePicker
            phone_field := ft.TextField(label="Número de Contacto", expand=True, on_change=lambda e: validate_phone(phone_field)),
            email_field := ft.TextField(label="Correo Electrónico", expand=True, on_change=lambda e: validate_email(email_field)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )

    # --- Sección de Datos Geográficos ---
    geographical_data_section = ft.Column(
        controls=[
            address_field := ft.TextField(label="Dirección", expand=True, on_change=lambda e: validate_address(address_field)),
            city_field := ft.TextField(label="Ciudad", expand=True, on_change=lambda e: validate_city(city_field)),
            state_field := ft.TextField(label="Estado", expand=True, on_change=lambda e: validate_state(state_field)),
            postal_code_field := ft.TextField(label="Código Postal", expand=True, on_change=lambda e: validate_postal_code(postal_code_field)),
            zone_field := ft.TextField(label="Zona a ser Atendida", expand=True, on_change=lambda e: validate_zone(zone_field)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )

    # --- Sección de Grupo Familiar ---
    family_group_section = ft.Column(
        controls=[
            family_members_field := ft.TextField(label="Número de Miembros", expand=True, on_change=lambda e: validate_family_members(family_members_field)),
            family_details_field := ft.TextField(label="Detalles de los Miembros", multiline=True, expand=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )

    # --- Sección de Detalles del Caso ---
    case_details_section = ft.Column(
        controls=[
            case_description_field := ft.TextField(label="Descripción de la Necesidad", multiline=True, expand=True, on_change=lambda e: validate_case_description(case_description_field)),
            aid_type_field := ft.TextField(label="Tipo de Ayuda Solicitada", expand=True, on_change=lambda e: validate_aid_type(aid_type_field)),
            urgency_field := ft.TextField(label="Urgencia", expand=True, on_change=lambda e: validate_urgency(urgency_field)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )

    # --- Botón de Envío ---
    def submit_form(e):
        """Valida todos los campos antes de enviar el formulario y guarda los datos en SQLite."""
        is_valid = True
        is_valid &= validate_name(name_field)
        is_valid &= validate_id(id_field)
        is_valid &= validate_phone(phone_field)
        is_valid &= validate_email(email_field)
        is_valid &= validate_address(address_field)
        is_valid &= validate_city(city_field)
        is_valid &= validate_state(state_field)
        is_valid &= validate_postal_code(postal_code_field)
        is_valid &= validate_zone(zone_field)
        is_valid &= validate_family_members(family_members_field)
        is_valid &= validate_case_description(case_description_field)
        is_valid &= validate_aid_type(aid_type_field)
        is_valid &= validate_urgency(urgency_field)

        if is_valid:
            print("Formulario válido. Enviando...")
            # Recopilar datos del formulario
            request_data = (
                name_field.value,
                id_field.value,
                birth_date_field.value,
                phone_field.value,
                email_field.value,
                address_field.value,
                city_field.value,
                state_field.value,
                postal_code_field.value,
                zone_field.value,
                family_members_field.value,
                family_details_field.value,
                case_description_field.value,
                aid_type_field.value,
                urgency_field.value,
            )
            # Insertar datos en la base de datos
            if conn:
                insert_request(conn, request_data)
                print("Datos guardados en la base de datos.")
                # Clear the form fields after successful submission
                name_field.value = ""
                id_field.value = ""
                birth_date_field.value = ""
                phone_field.value = ""
                email_field.value = ""
                address_field.value = ""
                city_field.value = ""
                state_field.value = ""
                postal_code_field.value = ""
                zone_field.value = ""
                family_members_field.value = ""
                family_details_field.value = ""
                case_description_field.value = ""
                aid_type_field.value = ""
                urgency_field.value = ""
                page.update()
        else:
            print("Formulario inválido. Revise los campos.")

    save_button = ft.ElevatedButton(text="Guardar", width=200, on_click=submit_form)

    # --- Pestañas ---
    tabs = ft.Tabs(
        expand=True,
        tabs=[
            ft.Tab(text="Datos Personales", content=personal_data_section),
            ft.Tab(text="Datos Geográficos", content=geographical_data_section),
            ft.Tab(text="Grupo Familiar", content=family_group_section),
            ft.Tab(text="Detalles del Caso", content=case_details_section),
        ],
    )

    # --- Formulario Principal ---
    main_form = ft.Column(
        controls=[
            save_button,
            ft.Divider(height=2, color="transparent"),
            tabs,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.add(main_form)

ft.app(target=main)
