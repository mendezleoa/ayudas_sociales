import flet as ft

def build_navigation_rail():
    """Crea y devuelve el NavigationRail (menú)."""
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.FloatingActionButton(
            icon=ft.icons.CREATE, 
            text="Add",
            on_click=lambda e: print("Add")
        ),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.LIST_ALT_OUTLINED,
                selected_icon=ft.icons.LIST_ALT,
                label="Ver Solicitudes Registradas",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=lambda e: handle_navigation_change(e),
    )
    return nav_rail
def handle_navigation_change(e):
    """Maneja los cambios de selección en el NavigationRail"""
    if e.control.selected_index == 1:  # Ver Solicitudes Registradas
        e.page.display_requests(e.page)