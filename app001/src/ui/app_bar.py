import flet as ft

def build_app_bar():
    """Crea y devuelve el AppBar."""
    return ft.AppBar(
        title=ft.Text("My Flet App"),
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(ft.icons.WB_SUNNY_OUTLINED),
        ],
    )
