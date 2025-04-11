# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\plantilla.py
import flet as ft
# Quitar import de build_app_bar y build_navigation_rail si no se usan aquí
# from ui.app_bar import build_app_bar
# from ui.menu import build_navigation_rail
from database import get_all_requests, create_connection

# Global State (simplificado) - Considerar encapsular en una clase si la app crece
search_term = ""
# Referencia global a la tabla para poder refrescarla desde fuera si es necesario
# (Aunque pasarla como argumento suele ser más limpio)
_data_table_instance = None

# --- Data Table Functions ---

def fill_data_table(page: ft.Page, data_table: ft.DataTable):
    """
    Obtiene datos de la base de datos 'solicitudes', los filtra
    y rellena la tabla principal.
    """
    global _data_table_instance
    _data_table_instance = data_table # Guardar referencia

    data_table.rows.clear() # Limpiar filas existentes
    conn = None
    new_rows = []

    try:
        conn = create_connection()
        if not conn:
            if page: # Solo mostrar snackbar si page está disponible
                 page.show_snack_bar(ft.SnackBar(ft.Text("Error: No se pudo conectar a la base de datos."), open=True))
            data_table.rows = []
            if data_table.page: data_table.update() # Actualizar si la tabla está en una página
            return

        requests = get_all_requests(conn)

        for req in requests:
            # Extraer datos relevantes (ajusta índices si tu SELECT cambia)
            id_val = str(req[0])
            nombre_val = req[1]
            identificacion_val = req[2]
            telefono_val = req[4] if req[4] else "-"
            ciudad_val = req[7]
            tipo_ayuda_val = req[14]
            urgencia_val = req[15]

            row_content_lower = f"{id_val} {nombre_val} {identificacion_val} {telefono_val} {ciudad_val} {tipo_ayuda_val} {urgencia_val}".lower()

            is_visible = True
            if search_term and search_term not in row_content_lower:
                is_visible = False

            if is_visible:
                new_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(id_val, color="black")),
                            ft.DataCell(ft.Text(nombre_val, color="black")),
                            ft.DataCell(ft.Text(identificacion_val, color="black")),
                            ft.DataCell(ft.Text(telefono_val, color="black")),
                            ft.DataCell(ft.Text(ciudad_val, color="black")),
                            ft.DataCell(ft.Text(tipo_ayuda_val, color="black")),
                            ft.DataCell(ft.Text(urgencia_val, color="black")),
                            # TODO: Añadir botones de acción (Ver/Editar/Eliminar)
                        ]
                    )
                )

    except Exception as e:
        print(f"Error al llenar la tabla: {e}")
        if page: # Solo mostrar snackbar si page está disponible
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Error al cargar datos: {e}"), open=True))
        new_rows = [ft.DataRow(cells=[ft.DataCell(ft.Text("Error al cargar datos", color="red", colspan=7))])]
    finally:
        if conn:
            conn.close()

    data_table.rows = new_rows
    if data_table.page: data_table.update() # Actualizar si la tabla está en una página

# --- UI Element Creation Functions ---
# create_search_field, create_search_bar se mantienen igual

def create_search_field(on_change_handler):
    """Crea el campo de texto para la búsqueda."""
    return ft.TextField(
        border_color="transparent",
        height=20,
        text_size=14,
        content_padding=0,
        cursor_color="white",
        cursor_width=1,
        color="white",
        hint_text="Buscar...",
        on_change=on_change_handler,
    )

def create_search_bar(search_field_control: ft.TextField):
    """Crea el contenedor de la barra de búsqueda."""
    return ft.Container(
        width=350,
        bgcolor="white10",
        border_radius=6,
        opacity=0,
        animate_opacity=300,
        padding=8,
        content=ft.Row(
            spacing=10,
            vertical_alignment="center",
            controls=[
                ft.Icon(name=ft.Icons.SEARCH_ROUNDED, size=17, opacity=0.85),
                search_field_control,
            ],
        ),
    )


# --- Event Handlers ---
# toggle_search se mantiene igual
def toggle_search(e: ft.HoverEvent, search_bar_control: ft.Container):
    """Muestra u oculta la barra de búsqueda al pasar el ratón sobre el header."""
    search_bar_control.opacity = 1 if e.data == "true" else 0
    search_bar_control.update()

# filter_dt_rows necesita page y data_table
def filter_dt_rows(e: ft.ControlEvent, page: ft.Page, data_table: ft.DataTable):
    """Actualiza el término de búsqueda y rellena la tabla."""
    global search_term
    search_term = e.control.value.lower().strip()
    fill_data_table(page, data_table) # Volver a llenar la tabla aplicando el filtro

# --- Main UI Building Functions ---
# build_header y build_data_table se mantienen igual en su estructura interna

def build_header(page: ft.Page, data_table: ft.DataTable):
    """Construye el encabezado con título y barra de búsqueda."""
    header_style = {
        "height": 60,
        "bgcolor": "#081d33",
        "border_radius": ft.border_radius.only(top_left=15, top_right=15),
        "padding": ft.padding.only(left=15, right=15),
    }
    search_on_change_handler = lambda event: filter_dt_rows(event, page, data_table)
    search_value_field = create_search_field(search_on_change_handler)
    search_bar_control = create_search_bar(search_value_field)
    header_container = ft.Container(
        **header_style,
        on_hover=lambda hover_event: toggle_search(hover_event, search_bar_control)
    )
    header_container.content = ft.Row(
        alignment="spaceBetween",
        controls=[
            ft.Text("Solicitudes Registradas", color="white"),
            search_bar_control,
        ],
    )
    return header_container

def build_data_table():
    """Construye la estructura inicial del DataTable para las solicitudes."""
    column_names = ["ID", "Nombre", "Identificación", "Teléfono", "Ciudad", "Tipo Ayuda", "Urgencia"]
    data_table_style = {
        "expand": True,
        "border_radius": 8,
        "border": ft.border.all(1, "#ebebeb"),
        "horizontal_lines": ft.border.BorderSide(1, "#ebebeb"),
        "columns": [
            ft.DataColumn(ft.Text(name, size=12, color="black", weight="bold"))
            for name in column_names
        ],
        "rows": [],
    }
    data_table = ft.DataTable(**data_table_style)
    return data_table

# --- Función para construir la VISTA ---
def build_solicitudes_view(page: ft.Page):
    """
    Construye el contenido de la vista de lista de solicitudes.

    Args:
        page: La instancia de la página (necesaria para handlers como SnackBar).

    Returns:
        ft.Control: El control principal (Column) que contiene esta vista.
    """
    data_table = build_data_table()
    header = build_header(page, data_table)

    # Cargar datos iniciales en la tabla *después* de crearla
    fill_data_table(page, data_table)

    # Contenido principal de esta vista
    view_content = ft.Column(
        expand=True,
        controls=[
            header,
            ft.Divider(height=5, color="transparent"),
            ft.Container(
                expand=True,
                padding=ft.padding.only(left=15, right=15, bottom=15),
                content=ft.Column(
                    scroll=ft.ScrollMode.HIDDEN,
                    expand=True,
                    controls=[
                        ft.Row(controls=[data_table])
                    ],
                )
            )
        ],
    )
    return view_content

# --- Bloque de prueba ---
def _test_main(page: ft.Page):
    """Función para probar esta vista de forma aislada."""
    page.title = "Test Vista Solicitudes"
    page.bgcolor = "#fdfdfd"
    page.padding = 10

    # Construye el contenido de la vista
    vista = build_solicitudes_view(page)

    # Añade el contenido a la página de prueba
    page.add(vista)
    page.update()

if __name__ == "__main__":
    # Opcional: Asegurar DB/Tabla
    # conn = create_connection()
    # if conn: create_table(conn); conn.close()
    ft.app(target=_test_main) # Ejecuta la función de prueba
