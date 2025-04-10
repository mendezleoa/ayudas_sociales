import flet as ft
from ui.app_bar import build_app_bar
from ui.menu import build_navigation_rail
from database import get_all_requests, create_connection, create_table

# Global State
dummy_data = {
    0: {"name": "Apple", "description": "Red and juicy", "quantity": 5, "price": 1.99},
    1: {
        "name": "Bread",
        "description": "Whole wheat loaf",
        "quantity": 2,
        "price": 3.49,
    },
    2: {
        "name": "Milk",
        "description": "Organic whole milk",
        "quantity": 1,
        "price": 2.99,
    },
    3: {
        "name": "Carrot",
        "description": "Fresh and crunchy",
        "quantity": 10,
        "price": 0.99,
    },
    4: {
        "name": "Eggs",
        "description": "Free-range brown eggs",
        "quantity": 12,
        "price": 2.79,
    },
    5: {
        "name": "Chicken",
        "description": "Boneless skinless breasts",
        "quantity": 2,
        "price": 7.99,
    },
    6: {
        "name": "Banana",
        "description": "Ripe and yellow",
        "quantity": 6,
        "price": 0.49,
    },
}

items = dummy_data
counter = len(items)
data_table_rows = []
search_term = ""


# --- Data Management Functions ---

def display_requests(page):
    """Muestra las solicitudes registradas en una tabla."""
    
    # Crear contenedor principal
    main_container = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text("Solicitudes Registradas", size=20, weight="bold"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Nombre")),
                        ft.DataColumn(ft.Text("Identificación")), 
                        ft.DataColumn(ft.Text("Teléfono")),
                        ft.DataColumn(ft.Text("Email")),
                        ft.DataColumn(ft.Text("Ciudad")),
                        ft.DataColumn(ft.Text("Tipo Ayuda")),
                        ft.DataColumn(ft.Text("Urgencia"))
                    ],
                    rows=[]
                )
            ]
        ),
        padding=20
    )
    
    # Obtener conexión y datos
    conn = create_connection()
    if conn:
        requests = get_all_requests(conn)
        table = main_container.content.controls[1]
        
        # Agregar filas a la tabla
        for req in requests:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(req[0]))),  # ID
                        ft.DataCell(ft.Text(req[1])),       # Nombre
                        ft.DataCell(ft.Text(req[2])),       # Identificación
                        ft.DataCell(ft.Text(req[4])),       # Teléfono
                        ft.DataCell(ft.Text(req[5])),       # Email
                        ft.DataCell(ft.Text(req[7])),       # Ciudad
                        ft.DataCell(ft.Text(req[14])),      # Tipo Ayuda
                        ft.DataCell(ft.Text(req[15]))       # Urgencia
                    ]
                )
            )
        conn.close()
        
    # Actualizar la página
    page.clean()
    page.add(main_container)
    page.update()

def get_items():
    return items

def add_item(data: dict):
    global counter
    items[counter] = data
    counter += 1

# --- UI Element Creation Functions ---


def create_search_field(on_change_function):
    return ft.TextField(
        border_color="transparent",
        height=20,
        text_size=14,
        content_padding=0,
        cursor_color="white",
        cursor_width=1,
        color="white",
        hint_text="Search",
        on_change=on_change_function,
    )


def create_search_bar(control: ft.TextField):
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
                ft.Icon(
                    name=ft.Icons.SEARCH_ROUNDED,
                    size=17,
                    opacity=0.85,
                ),
                control,
            ],
        ),
    )


def create_text_field():
    return ft.TextField(
        border_color="transparent",
        height=20,
        text_size=13,
        content_padding=0,
        cursor_color="black",
        cursor_width=1,
        cursor_height=18,
        color="black",
    )


def create_text_field_container(expand: bool | int, name: str, control: ft.TextField):
    return ft.Container(
        expand=expand,
        height=45,
        bgcolor="#ebebeb",
        border_radius=6,
        padding=8,
        content=ft.Column(
            spacing=1,
            controls=[
                ft.Text(value=name, size=9, color="black", weight="bold"),
                control,
            ],
        ),
    )


# --- Event Handlers ---


def toggle_search(e: ft.HoverEvent, search_bar_control):
    search_bar_control.opacity = 1 if e.data == "true" else 0
    search_bar_control.update()


def filter_dt_rows(e, data_table):
    global search_term
    search_term = e.control.value.lower()
    fill_data_table(data_table)


def submit_data(
    e: ft.TapEvent,
    row1_value,
    row2_value,
    row3_value,
    row4_value,
    data_table,
    form_content,
):
    data = {
        "col1": row1_value.value,
        "col2": row2_value.value,
        "col3": row3_value.value,
        "col4": row4_value.value,
    }

    add_item(data)
    clear_entries(row1_value, row2_value, row3_value, row4_value, form_content)
    fill_data_table(data_table)


def clear_entries(row1_value, row2_value, row3_value, row4_value, form_content):
    row1_value.value = ""
    row2_value.value = ""
    row3_value.value = ""
    row4_value.value = ""
    form_content.update()


# --- Data Table Functions ---


def fill_data_table(data_table):
    global data_table_rows
    data_table.rows.clear()
    data_table_rows = []

    for values in items.values():
        data_cells = [
            ft.DataCell(ft.Text(value, color="black")) for value in values.values()
        ]
        data_row = ft.DataRow(cells=data_cells, visible=True)
        if search_term:
            data_row.visible = search_term in data_row.cells[0].content.value.lower()
        data_table_rows.append(data_row)

    data_table.rows = data_table_rows
    data_table.update()


# --- Main UI Building Functions ---


def build_header(data_table):
    header_style = {
        "height": 60,
        "bgcolor": "#081d33",
        "border_radius": ft.border_radius.only(top_left=15, top_right=15),
        "padding": ft.padding.only(left=15, right=15),
    }

    search_value = create_search_field(lambda e: filter_dt_rows(e, data_table))
    search_bar_control = create_search_bar(search_value)

    header_container = ft.Container(
        **header_style, on_hover=lambda e: toggle_search(e, search_bar_control)
    )
    header_container.content = ft.Row(
        alignment="spaceBetween",
        controls=[
            ft.Text("Line Indent"),
            search_bar_control,
            ft.IconButton("person"),
        ],
    )

    return header_container


def build_form(data_table):
    form_style = {
        "border_radius": 8,
        "border": ft.border.all(1, "#ebebeb"),
        "bgcolor": "white10",
        "padding": 15,
    }

    row1_value = create_text_field()
    row2_value = create_text_field()
    row3_value = create_text_field()
    row4_value = create_text_field()

    row1 = create_text_field_container(True, "Row One", row1_value)
    row2 = create_text_field_container(3, "Row Two", row2_value)
    row3 = create_text_field_container(1, "Row Three", row3_value)
    row4 = create_text_field_container(1, "Row Four", row4_value)

    submit_button = ft.ElevatedButton(
        text="Submit",
        style=ft.ButtonStyle(shape={"": ft.RoundedRectangleBorder(radius=8)}),
        on_click=lambda e: submit_data(
            e, row1_value, row2_value, row3_value, row4_value, data_table, form_content
        ),
    )

    form_content = ft.Column(
        expand=True,
        controls=[
            ft.Row(controls=[row1]),
            ft.Row(controls=[row2, row3, row4]),
            ft.Row(controls=[submit_button], alignment="end"),
        ],
    )

    form_container = ft.Container(**form_style, content=form_content)
    return form_container, form_content, row1_value, row2_value, row3_value, row4_value


def build_data_table():
    column_names = ["Column One", "Column Two", "Column Three", "Column Four"]

    data_table_style = {
        "expand": True,
        "border_radius": 8,
        "border": ft.border.all(2, "#ebebeb"),
        "horizontal_lines": ft.border.BorderSide(1, "#ebebeb"),
        "columns": [
            ft.DataColumn(ft.Text(index, size=12, color="black", weight="bold"))
            for index in column_names
        ],
    }

    data_table = ft.DataTable(**data_table_style, rows=[])
    return data_table


def main(page: ft.Page):
    page.bgcolor = "#fdfdfd"
    # Add the appbar
    page.appbar = build_app_bar()

    data_table = build_data_table()
    header = build_header(data_table)
    form, form_content, row1_value, row2_value, row3_value, row4_value = build_form(
        data_table
    )

    # Navigation Rail
    rail = build_navigation_rail()

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    expand=True,
                    controls=[
                        header,
                        ft.Divider(height=2, color="transparent"),
                        form,
                        ft.Column(
                            scroll="hidden",
                            expand=True,
                            controls=[ft.Row(controls=[data_table])],
                        ),
                    ],
                ),
            ],
            expand=True,
        )
    )

    page.update()
    fill_data_table(data_table)


ft.app(target=main)
