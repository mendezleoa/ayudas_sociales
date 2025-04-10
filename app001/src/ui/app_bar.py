import flet as ft

def build_app_bar():
    """Crea y devuelve el AppBar."""
    return ft.AppBar(
        title=ft.Text("My Flet App"),
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        actions=[
            ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED),
        ],
    )
