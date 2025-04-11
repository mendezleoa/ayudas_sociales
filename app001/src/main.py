# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\main.py
import flet as ft

# --- Importar componentes de UI ---
from ui.app_bar import build_app_bar
# Importar todas las constantes de vista desde menu.py
from ui.menu import (
    build_navigation_rail,
    VIEW_HOME,
    VIEW_SOLICITUDES_LIST,
    VIEW_SETTINGS,
    VIEW_MANAGE_AID_TYPES, # <-- Índice para gestionar tipos de ayuda
    VIEW_ADD_SOLICITUD
)

# --- Importar constructores de Vistas ---
from plantilla import build_solicitudes_view, fill_data_table, _data_table_instance
from solicitud import build_solicitud_form_view
# Asegúrate de que la importación de AidTypesView sea correcta
from aid_types import AidTypesView

# --- Importar funciones de Base de Datos (para inicialización) ---
from database import create_connection, create_table

# --- Estado Global Simple ---
# Contenedor principal donde se mostrarán las vistas
view_container = ft.Container(expand=True, padding=ft.padding.all(15))
# Variables para almacenar las instancias de las vistas y evitar recrearlas innecesariamente
solicitudes_list_view = None
solicitud_form_view = None
settings_view = None
aid_types_crud_view = None # <-- Variable para la instancia de la vista CRUD

# --- Funciones de Autenticación (sin cambios) ---
def authenticate(username, password):
    """Verifica si el usuario y la contraseña son correctos."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            result = cursor.fetchone()
            if result:
                print(f"Autenticación exitosa para {username}. Rol: {result[0]}")
                return result[0] # Devuelve el rol
            else:
                print(f"Autenticación fallida para {username}: Usuario o contraseña incorrectos.")
                return None
        except Exception as e:
            print(f"Error durante la autenticación: {e}")
            return None
        finally:
            conn.close()
            print("Conexión cerrada después de autenticar.")
    else:
        print("Error: No se pudo conectar a la base de datos para autenticar.")
        return None

# --- Función de Cambio de Vista (ACTUALIZADA) ---
def change_view(page: ft.Page, index: int):
    """
    Cambia la vista mostrada en el contenedor principal basado en el índice
    recibido desde el NavigationRail.
    """
    # Hacemos referencia a las variables globales que almacenan las vistas
    global view_container, solicitudes_list_view, solicitud_form_view, settings_view, aid_types_crud_view

    print(f"Navegando a la vista con índice: {index}")

    # Limpiar el contenido actual antes de mostrar la nueva vista
    view_container.content = ft.ProgressRing() # Mostrar un indicador de carga temporal
    view_container.update()

    # Seleccionar qué vista mostrar según el índice
    content_to_display = None

    if index == VIEW_HOME or index == VIEW_SOLICITUDES_LIST: # 0 o 1
        print("Mostrando vista: Lista de Solicitudes")
        if not solicitudes_list_view:
             print("Creando instancia de solicitudes_list_view...")
             solicitudes_list_view = build_solicitudes_view(page)
        # Refrescar datos de la tabla de solicitudes si ya existe
        if _data_table_instance:
            print("Refrescando datos de la tabla de solicitudes...")
            fill_data_table(page, _data_table_instance)
        content_to_display = solicitudes_list_view

    elif index == VIEW_ADD_SOLICITUD: # 99 (Botón Add)
        print("Mostrando vista: Formulario Nueva Solicitud")
        if not solicitud_form_view:
            print("Creando instancia de solicitud_form_view...")
            try:
                # Intentar construir la vista del formulario
                solicitud_form_view = build_solicitud_form_view(page)
                print("Instancia de solicitud_form_view creada.")
            except Exception as e:
                print(f"*** ERROR CRÍTICO al construir solicitud_form_view: {e} ***")
                # Mostrar un mensaje de error en lugar del formulario si falla la construcción
                solicitud_form_view = ft.Column([
                    ft.Text("Error al Cargar Formulario", size=20, color=ft.colors.RED),
                    ft.Text(f"Detalle: {e}"),
                ])
        # Aquí podrías añadir lógica para limpiar el formulario si es necesario
        # if hasattr(solicitud_form_view, 'clear_form'):
        #     solicitud_form_view.clear_form()
        content_to_display = solicitud_form_view

    elif index == VIEW_SETTINGS: # 2
        print("Mostrando vista: Configuración")
        if not settings_view:
            print("Creando instancia de settings_view...")
            # Vista de configuración simple por ahora
            settings_view = ft.Column([ft.Text("Configuración General", size=20)])
        content_to_display = settings_view

    elif index == VIEW_MANAGE_AID_TYPES: # 3 (NUEVA VISTA CRUD)
        print("Mostrando vista: Gestión Tipos de Ayuda")
        if not aid_types_crud_view:
            print("Creando instancia de aid_types_crud_view por primera vez...")
            # Crear la instancia de la vista CRUD si no existe
            aid_types_crud_view = AidTypesView(page)
        else:
            # Si ya existe, refrescar sus datos para mostrar la información más reciente
            print("Refrescando datos de aid_types_crud_view...")
            # Verificar que el método exista antes de llamarlo
            if hasattr(aid_types_crud_view, 'refresh_data') and callable(aid_types_crud_view.refresh_data):
                 aid_types_crud_view.refresh_data()
            else:
                 print("Advertencia: El método 'refresh_data' no se encontró o no es llamable en AidTypesView.")
        content_to_display = aid_types_crud_view

    else:
        # Caso para índices desconocidos
        print(f"Índice de vista desconocido: {index}")
        content_to_display = ft.Text(f"Vista no encontrada para el índice {index}", color=ft.colors.ORANGE)

    # Asignar la vista seleccionada al contenedor y actualizar
    view_container.content = content_to_display
    view_container.update()
    print("Vista actualizada en el contenedor.")


# --- Construcción de la Interfaz Principal (ACTUALIZADA) ---
def build_main_app_view(page: ft.Page):
    """Construye y muestra la interfaz principal de la aplicación después del login."""
    # Hacemos referencia a las variables globales que almacenan las vistas
    global view_container, solicitudes_list_view, solicitud_form_view, settings_view, aid_types_crud_view

    print("Iniciando construcción de la vista principal de la aplicación...")

    page.clean() # Limpiar la vista de login
    page.title = "Sistema de Gestión de Ayudas Sociales"
    # Restablecer alineaciones y padding para la vista principal
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.padding = 0 # Sin padding en la página principal, el contenedor lo maneja
    page.window_width = 1150 # Ancho sugerido
    page.window_height = 800 # Alto sugerido

    # --- Construcción inicial de las vistas principales ---
    # Es buena idea intentar construir las vistas más usadas al inicio
    # para que la navegación sea más rápida la primera vez.
    # Manejar posibles errores durante la construcción.
    if not solicitudes_list_view:
        try:
            print("Construyendo vista 'Lista Solicitudes'...")
            solicitudes_list_view = build_solicitudes_view(page)
        except Exception as e:
            print(f"Error construyendo solicitudes_list_view: {e}")
            solicitudes_list_view = ft.Text(f"Error al cargar lista: {e}", color=ft.colors.RED)

    if not solicitud_form_view:
         try:
            print("Construyendo vista 'Formulario Solicitud'...")
            solicitud_form_view = build_solicitud_form_view(page)
         except Exception as e:
            print(f"Error construyendo solicitud_form_view: {e}")
            # Guardamos un control de error para mostrar si se intenta navegar aquí
            solicitud_form_view = ft.Text(f"Error al cargar formulario: {e}", color=ft.colors.RED)

    # La vista aid_types_crud_view se creará bajo demanda en change_view

    # --- Construir componentes fijos de la UI ---
    app_bar = build_app_bar()
    # Pasar la función change_view como handler al menú
    navigation_rail = build_navigation_rail(lambda idx: change_view(page, idx))

    # --- Ensamblar la página ---
    page.appbar = app_bar
    page.add(
        ft.Row(
            [
                navigation_rail, # Menú lateral
                ft.VerticalDivider(width=1), # Separador visual
                view_container, # Contenedor donde cambian las vistas
            ],
            expand=True, # Ocupar todo el espacio disponible
        )
    )

    # Mostrar la vista inicial por defecto (Lista de Solicitudes)
    print("Estableciendo vista inicial...")
    # Usamos el índice definido en menu.py para la vista inicial
    initial_view_index = VIEW_SOLICITUDES_LIST
    # Seleccionar visualmente la opción en el menú
    navigation_rail.selected_index = initial_view_index
    # Cargar el contenido de la vista inicial
    change_view(page, initial_view_index)

    page.update() # Actualizar la página para mostrar todo
    print("Vista principal construida y mostrada.")


# --- Construcción de la Interfaz de Login (sin cambios significativos) ---
def build_login_view(page: ft.Page, on_login_success):
    """Construye y muestra la interfaz de login."""
    page.clean() # Limpiar por si acaso
    page.title = "Ayudas Sociales - Inicio de Sesión"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 400 # Un poco más de espacio vertical
    page.padding = 20

    welcome_message = ft.Text("Bienvenido al Sistema", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    username_field = ft.TextField(label="Usuario", width=300, autofocus=True, border_radius=8)
    password_field = ft.TextField(
        label="Contraseña", password=True, can_reveal_password=True, width=300,
        on_submit=lambda e: login_clicked(e), # Permitir login con Enter
        border_radius=8
    )
    login_button = ft.ElevatedButton(text="Iniciar Sesión", width=300, height=40)
    error_message = ft.Text("", color=ft.colors.RED, text_align=ft.TextAlign.CENTER, visible=False)

    def login_clicked(e):
        """Maneja el evento de clic en el botón de Iniciar Sesión."""
        username = username_field.value.strip()
        password = password_field.value
        error_message.visible = False # Ocultar error previo
        page.update()

        if not username or not password:
            error_message.value = "Usuario y contraseña son requeridos."
            error_message.visible = True
            page.update()
            return

        role = authenticate(username, password) # Llama a la función de autenticación

        if role:
            # Si la autenticación es exitosa, llama a la función para construir la app principal
            on_login_success(page)
        else:
            # Si falla, muestra mensaje de error
            error_message.value = "Usuario o contraseña incorrectos."
            error_message.visible = True
            password_field.value = "" # Limpiar contraseña
            password_field.focus() # Poner foco de nuevo en contraseña
            page.update()

    login_button.on_click = login_clicked

    page.add(
        ft.Column(
            [
                welcome_message,
                ft.Divider(height=30, color="transparent"),
                username_field,
                password_field,
                ft.Divider(height=20, color="transparent"),
                login_button,
                error_message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, # Centrar verticalmente
            spacing=15,
            expand=True # Ocupar espacio vertical
        )
    )
    page.update()
    print("Vista de login mostrada.")


# --- Punto de Entrada Principal ---
def main(page: ft.Page):
    """Función principal que se pasa a ft.app()."""
    # Iniciar mostrando la vista de login.
    # Pasamos build_main_app_view como la función a llamar si el login es exitoso.
    build_login_view(page, build_main_app_view)

# --- Ejecución de la Aplicación ---
if __name__ == "__main__":
    print("Iniciando aplicación...")
    print("Verificando base de datos...")
    conn = None
    try:
        conn = create_connection()
        if conn:
            # Asegura que todas las tablas (incluida tipos_ayuda) existan
            create_table(conn)
            print("Base de datos verificada y lista.")
        else:
            # Si la conexión falla aquí, es un problema grave.
            print("¡ERROR CRÍTICO! No se pudo conectar/crear la base de datos al inicio.")
            # Podrías mostrar un error en Flet o simplemente salir.
            # ft.app(target=lambda page: page.add(ft.Text("Error crítico de base de datos")))
            exit(1) # Salir con código de error
    except Exception as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        exit(1)
    finally:
        if conn:
            conn.close()
            print("Conexión de verificación inicial cerrada.")

    # Iniciar la aplicación Flet
    ft.app(target=main)
    print("Aplicación finalizada.")
