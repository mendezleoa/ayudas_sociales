import flet as ft

def build_navigation_rail():
    """Crea y devuelve el NavigationRail (menú)."""
    return ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.FloatingActionButton(
            icon=ft.icons.CREATE, text="Add", on_click=lambda e: print("Add")
        ),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.BOOKMARK_BORDER,
                selected_icon=ft.icons.BOOKMARK,
                label="Bookmark",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.SETTINGS_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label="Settings",
            ),
        ],
        on_change=lambda e: print("Selected destination:", e.control.selected_index),
    )
