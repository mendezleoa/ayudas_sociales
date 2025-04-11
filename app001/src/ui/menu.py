# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\ui\menu.py
import flet as ft

# Definimos constantes para los índices para mayor claridad
VIEW_HOME = 0
VIEW_SOLICITUDES_LIST = 1
VIEW_SETTINGS = 2
VIEW_MANAGE_AID_TYPES = 3 # <-- Nuevo índice para gestionar tipos de ayuda
VIEW_ADD_SOLICITUD = 99 # Un índice especial o diferente para el botón Add

def build_navigation_rail(on_change_handler):
    """
    Crea y devuelve el NavigationRail (menú).

    Args:
        on_change_handler: La función a llamar cuando cambia la selección
                           o se hace clic en el botón Add. Debe aceptar el
                           índice de la vista a mostrar.
    """
    nav_rail = ft.NavigationRail(
        selected_index=VIEW_SOLICITUDES_LIST, # Iniciar en la lista de solicitudes
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            text="",
            tooltip="Registrar Nueva Solicitud",
            # Llama al handler con un índice específico para "Añadir"
            on_click=lambda e: on_change_handler(VIEW_ADD_SOLICITUD)
        ),
        group_alignment=-0.9,
        destinations=[
            # --- Opción 0: Home (Podría ser un Dashboard o la misma lista) ---
            # Por ahora, lo dirigimos a la lista también.
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Inicio", # Cambiado a Español
            ),
            # --- Opción 1: Ver Solicitudes ---
            ft.NavigationRailDestination(
                icon=ft.Icons.LIST_ALT_OUTLINED,
                selected_icon=ft.Icons.LIST_ALT,
                label="Ver Solicitudes", # Más corto
            ),
            # --- Opción 2: Settings (Configuración) ---
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Configuración", # Cambiado a Español
            ),
            # --- Opción 3: Gestionar Tipos de Ayuda (NUEVO) ---
            ft.NavigationRailDestination(
                icon=ft.Icons.CATEGORY_OUTLINED, # Icono sugerido
                selected_icon=ft.Icons.CATEGORY, # Icono sugerido
                label="Tipos Ayuda", # Etiqueta para la nueva opción
            ),
        ],
        # Llama al handler con el índice seleccionado
        on_change=lambda e: on_change_handler(e.control.selected_index),
    )
    return nav_rail

# La función handle_navigation_change ya no es necesaria aquí,
# la lógica se pasa directamente al on_change del NavigationRail
# y se maneja en la función 'on_change_handler' que se pasa desde fuera.
