# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\solicitud.py
import flet as ft
import re
import sqlite3
# Asegúrate que database.py tiene create_connection, create_table, insert_family_member
from database import create_connection, create_table, insert_family_member

# --- Importar validadores ---
from validators import validate_required, validate_phone, validate_email, validate_numeric

# --- Database Functions ---

def insert_request(conn, request_data):
    """
    Inserta una nueva solicitud en la tabla 'solicitudes'.
    Devuelve el ID de la fila insertada o None en caso de error.
    """
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
        # Asegúrate que request_data tenga 15 elementos (?)
        cursor.execute(sql, request_data)
        conn.commit()
        return cursor.lastrowid # Devolver el ID de la solicitud insertada
    except sqlite3.Error as e:
        print(f"Error al insertar la solicitud: {e}")
        conn.rollback() # Deshacer cambios en caso de error
        return None # Indicar fallo

# get_all_requests no es necesaria en este archivo si solo es para el formulario
# def get_all_requests(conn): ...

# --- UI Building Functions ---
# build_personal_data_section, build_geographical_data_section, build_case_details_section
# se mantienen estructuralmente iguales, pero ya no necesitan expand=True en el Container principal
# si la columna que los contiene ya se expande.

def build_personal_data_section():
    name_field = ft.TextField(label="Nombre Completo*", expand=True)
    id_field = ft.TextField(label="Número de Identificación*", expand=True)
    birth_date_field = ft.TextField(label="Fecha de Nacimiento", hint_text="DD/MM/AAAA", expand=True)
    phone_field = ft.TextField(label="Número de Contacto*", expand=True, keyboard_type=ft.KeyboardType.PHONE, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"))
    email_field = ft.TextField(label="Correo Electrónico", expand=True, keyboard_type=ft.KeyboardType.EMAIL)

    name_field.on_change = lambda e: validate_required(name_field, "Nombre")
    id_field.on_change = lambda e: validate_required(id_field, "Identificación")
    phone_field.on_change = lambda e: validate_phone(phone_field)
    email_field.on_change = lambda e: validate_email(email_field)

    return ft.Container(
        padding=10,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row([name_field, id_field]),
                ft.Row([birth_date_field]),
                ft.Row([phone_field, email_field]),
            ],
        )
    ), name_field, id_field, birth_date_field, phone_field, email_field

def build_geographical_data_section():
    address_field = ft.TextField(label="Dirección Completa*", expand=True, multiline=True, max_lines=3)
    city_field = ft.TextField(label="Ciudad*", expand=1)
    state_field = ft.TextField(label="Estado/Provincia*", expand=1)
    postal_code_field = ft.TextField(label="Código Postal*", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    zone_field = ft.TextField(label="Zona/Barrio/Sector*", expand=True)

    address_field.on_change = lambda e: validate_required(address_field, "Dirección")
    city_field.on_change = lambda e: validate_required(city_field, "Ciudad")
    state_field.on_change = lambda e: validate_required(state_field, "Estado")
    postal_code_field.on_change = lambda e: validate_required(postal_code_field, "Código Postal")
    zone_field.on_change = lambda e: validate_required(zone_field, "Zona")

    return ft.Container(
        padding=ft.padding.all(15),
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([address_field]),
                ft.Row([city_field, state_field, postal_code_field]),
                ft.Row([zone_field]),
            ],
        )
    ), address_field, city_field, state_field, postal_code_field, zone_field

# Modificado para aceptar 'page'
def build_family_group_section(page: ft.Page):
    """Construye la sección de grupo familiar del formulario."""
    family_members_field = ft.TextField(
        label="Número de Miembros*",
        expand=1,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]")
    )

    # Lista para mantener referencias a los contenedores de miembros
    member_containers = []
    # Columna donde se añadirán/quitarán los campos de miembros
    members_column = ft.Column(
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        # expand=True # La expansión debe manejarla el contenedor padre (Tabs)
    )

    def add_member_fields():
        """Crea y retorna un contenedor con campos para un miembro familiar."""
        # Crear los TextFields para este miembro
        nombre_miembro = ft.TextField(label="Nombre Completo*", expand=True)
        id_miembro = ft.TextField(label="Identificación*", expand=True)
        relacion_miembro = ft.TextField(label="Relación/Parentesco*", expand=True)
        nacimiento_miembro = ft.TextField(label="Fecha de Nacimiento", hint_text="DD/MM/AAAA", expand=True)
        condiciones_miembro = ft.TextField(label="Condiciones Especiales", multiline=True, min_lines=2, max_lines=3, expand=True)

        # Crear el contenedor para agruparlos
        member_container = ft.Container(
            # Guardar referencias a los campos dentro del contenedor para fácil acceso
            data={
                "nombre": nombre_miembro,
                "id": id_miembro,
                "relacion": relacion_miembro,
                "nacimiento": nacimiento_miembro,
                "condiciones": condiciones_miembro,
            },
            content=ft.Column([
                nombre_miembro,
                id_miembro,
                relacion_miembro,
                nacimiento_miembro,
                condiciones_miembro,
                ft.Divider(height=10, color="transparent"),
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=8,
            margin=ft.margin.only(bottom=10)
        )
        member_containers.append(member_container) # Añadir a la lista global de esta sección
        return member_container

    def update_member_fields(e):
        """Actualiza los campos de miembros según el número ingresado."""
        try:
            num_members = int(family_members_field.value or 0)
            current_members = len(member_containers)

            if num_members > current_members:
                for _ in range(num_members - current_members):
                    members_column.controls.append(add_member_fields())
            elif num_members < current_members:
                for _ in range(current_members - num_members):
                    member_containers.pop()
                    members_column.controls.pop()

            # Usar la 'page' pasada a build_family_group_section
            if page: page.update()

        except ValueError:
            # Opcional: Mostrar error si no es un número
            family_members_field.error_text = "Ingrese un número válido"
            if page: page.update()
        else:
            # Limpiar error si el valor es válido
            family_members_field.error_text = None
            if page: page.update()


    family_members_field.on_change = update_member_fields

    return ft.Container(
        padding=ft.padding.all(15),
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([family_members_field]),
                members_column, # La columna dinámica
            ],
        )
    ), family_members_field, member_containers # Devolver la lista de contenedores

def build_case_details_section():
    case_description_field = ft.TextField(label="Descripción Detallada*", multiline=True, min_lines=3, max_lines=5, expand=True)
    tipos_ayuda = ["Alimentos", "Vivienda", "Salud", "Educación", "Empleo", "Otro"]
    urgencias = ["Crítica (Inmediata)", "Alta (Próximos días)", "Media (Próximas semanas)", "Baja (Sin urgencia inmediata)"]
    aid_type_dropdown = ft.Dropdown(label="Tipo de Ayuda Solicitada*", options=[ft.dropdown.Option(tipo) for tipo in tipos_ayuda], expand=True)
    urgency_dropdown = ft.Dropdown(label="Nivel de Urgencia*", options=[ft.dropdown.Option(urg) for urg in urgencias], expand=True)

    case_description_field.on_change = lambda e: validate_required(case_description_field, "Descripción")
    aid_type_dropdown.on_change = lambda e: validate_required(aid_type_dropdown, "Tipo de ayuda")
    urgency_dropdown.on_change = lambda e: validate_required(urgency_dropdown, "Urgencia")

    return ft.Container(
        padding=ft.padding.all(15),
        content=ft.Column(
            spacing=15,
            controls=[
                ft.Row([case_description_field]),
                ft.Row([aid_type_dropdown, urgency_dropdown]),
            ],
        )
    ), case_description_field, aid_type_dropdown, urgency_dropdown


# --- Función para construir la VISTA ---
def build_solicitud_form_view(page: ft.Page):
    """
    Construye el contenido de la vista del formulario de solicitud.

    Args:
        page: La instancia de la página (necesaria para SnackBar y updates).

    Returns:
        ft.Control: El control principal (Column) que contiene esta vista.
    """
    # --- Construir Secciones y obtener referencias a los campos ---
    personal_section_content, name_f, id_f, birth_f, phone_f, email_f = build_personal_data_section()
    geo_section_content, address_f, city_f, state_f, postal_f, zone_f = build_geographical_data_section()
    # Pasar 'page' a la sección de familia
    family_section_content, members_f, member_containers_list = build_family_group_section(page)
    case_section_content, desc_f, aid_dd, urgency_dd = build_case_details_section()

    # --- Funciones Internas (Handlers y Lógica) ---
    def clear_form():
        fields_to_clear = [
            name_f, id_f, birth_f, phone_f, email_f, address_f, city_f,
            state_f, postal_f, zone_f, members_f, desc_f
        ]
        dropdowns_to_clear = [aid_dd, urgency_dd]

        for field in fields_to_clear:
            field.value = ""
            field.error_text = None
        for dropdown in dropdowns_to_clear:
            dropdown.value = None
            dropdown.error_text = None

        # Limpiar también los campos de miembros familiares
        for container in member_containers_list:
            for field in container.data.values(): # Acceder a los campos guardados en 'data'
                 if hasattr(field, 'value'): field.value = ""
                 if hasattr(field, 'error_text'): field.error_text = None
        # Resetear el número de miembros y limpiar la columna visualmente
        members_f.value = "0" # O "" si prefieres
        update_member_fields(None) # Llamar para limpiar visualmente (requiere adaptar update_member_fields para manejar e=None)

        if page: page.update()

    def show_snackbar(message, color):
        """Función auxiliar para mostrar SnackBars."""
        if page:
            snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def submit_form(e):
        # Validar campos principales
        is_valid = True
        is_valid &= validate_required(name_f, "Nombre")
        is_valid &= validate_required(id_f, "Identificación")
        is_valid &= validate_phone(phone_f)
        is_valid &= validate_email(email_f) # Asume opcional
        is_valid &= validate_required(address_f, "Dirección")
        is_valid &= validate_required(city_f, "Ciudad")
        is_valid &= validate_required(state_f, "Estado")
        is_valid &= validate_required(postal_f, "Código Postal")
        is_valid &= validate_required(zone_f, "Zona")
        is_valid &= validate_numeric(members_f, "Número de miembros")
        is_valid &= validate_required(desc_f, "Descripción")
        is_valid &= validate_required(aid_dd, "Tipo de ayuda")
        is_valid &= validate_required(urgency_dd, "Urgencia")

        # Validar campos de miembros familiares (si los hay)
        num_members_val = int(members_f.value or 0)
        if num_members_val > 0:
            for i, container in enumerate(member_containers_list):
                member_name = container.data["nombre"]
                member_id = container.data["id"]
                member_rel = container.data["relacion"]
                is_valid &= validate_required(member_name, f"Nombre Miembro {i+1}")
                is_valid &= validate_required(member_id, f"ID Miembro {i+1}")
                is_valid &= validate_required(member_rel, f"Relación Miembro {i+1}")

        if not is_valid:
            show_snackbar("Formulario inválido. Revise los campos marcados.", ft.colors.RED_400)
            if page: page.update() # Asegurar que los errores de validación se muestren
            return

        # --- Si es válido, proceder con la base de datos ---
        request_data = (
            name_f.value, id_f.value, birth_f.value, phone_f.value, email_f.value,
            address_f.value, city_f.value, state_f.value, postal_f.value, zone_f.value,
            num_members_val,
            None, # detalles_miembros (campo de texto original, ahora manejado en tabla separada) - Podrías quitarlo de la tabla solicitudes
            desc_f.value, aid_dd.value, urgency_dd.value,
        )

        conn = None
        solicitud_insertada = False
        try:
            conn = create_connection()
            if not conn:
                show_snackbar("Error: No se pudo conectar a la base de datos.", ft.colors.RED_200)
                return

            # Insertar solicitud principal
            last_solicitud_id = insert_request(conn, request_data)

            if last_solicitud_id:
                # Insertar miembros familiares
                for container in member_containers_list:
                    member_data = (
                        last_solicitud_id,
                        container.data["nombre"].value,
                        container.data["id"].value,
                        container.data["relacion"].value,
                        container.data["nacimiento"].value, # Puede ser None
                        container.data["condiciones"].value, # Puede ser None
                    )
                    if not insert_family_member(conn, member_data):
                        # Error insertando miembro, deshacer todo y mostrar error
                        conn.rollback()
                        show_snackbar(f"Error guardando miembro: {container.data['nombre'].value}", ft.colors.RED_200)
                        solicitud_insertada = False
                        break # Salir del bucle de miembros
                else: # Se ejecuta si el bucle de miembros terminó sin break (sin errores)
                    conn.commit() # Confirmar transacción completa (solicitud + miembros)
                    solicitud_insertada = True
            else:
                # Error insertando la solicitud principal
                show_snackbar("Error al guardar la solicitud principal.", ft.colors.RED_200)

        except Exception as db_error:
            print(f"Error de base de datos durante el envío: {db_error}")
            if conn: conn.rollback() # Intentar deshacer si hubo excepción
            show_snackbar(f"Error inesperado en base de datos: {db_error}", ft.colors.RED_200)
        finally:
            if conn:
                conn.close()

        if solicitud_insertada:
            show_snackbar("Solicitud guardada exitosamente.", ft.colors.GREEN_200)
            clear_form() # Limpiar formulario (ya llama a page.update)
        # Los mensajes de error ya se mostraron dentro del try/except

    # --- Construir UI de la Vista ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True, # Permitir que las pestañas llenen el espacio
        tabs=[
            ft.Tab(text="1. Datos Personales", content=personal_section_content),
            ft.Tab(text="2. Datos Geográficos", content=geo_section_content),
            ft.Tab(text="3. Grupo Familiar", content=family_section_content),
            ft.Tab(text="4. Detalles del Caso", content=case_section_content),
        ],
    )

    save_button = ft.ElevatedButton(
        text="Guardar Solicitud",
        icon=ft.Icons.SAVE_ALT_OUTLINED,
        on_click=submit_form,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(vertical=12, horizontal=20)
        ),
    )

    # Contenido principal de esta vista
    view_content = ft.Column(
        expand=True, # La columna principal debe expandirse
        scroll=ft.ScrollMode.ADAPTIVE, # Permitir scroll si el contenido excede
        controls=[
            ft.Text("Formulario de Registro de Solicitud", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color="transparent"),
            ft.Row([save_button], alignment=ft.MainAxisAlignment.END),
            tabs, # Las pestañas ocuparán el espacio restante gracias a expand=True en Tabs y Column
            ft.Divider(height=10, color="transparent"),
        ]
    )

    return view_content

# --- Bloque de prueba ---
def _test_main(page: ft.Page):
    """Función para probar esta vista de forma aislada."""
    page.title = "Test Formulario Solicitud"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = ft.padding.all(20)
    # page.scroll = ft.ScrollMode.ADAPTIVE # El scroll se maneja en la columna devuelta

    # Asegurar que la tabla exista para la prueba
    conn = create_connection()
    if conn:
        create_table(conn) # Crea ambas tablas si no existen
        conn.close()
    else:
        page.add(ft.Text("Error conectando a DB para prueba"))
        return

    # Construye el contenido de la vista
    vista = build_solicitud_form_view(page)

    # Añade el contenido a la página de prueba
    page.add(vista)
    page.update()

if __name__ == "__main__":
    ft.app(target=_test_main)
