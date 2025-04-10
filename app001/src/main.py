# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\main.py
import flet as ft

# --- Importar componentes de UI ---
from ui.app_bar import build_app_bar
from ui.menu import build_navigation_rail, VIEW_SOLICITUDES_LIST, VIEW_ADD_SOLICITUD, VIEW_SETTINGS, VIEW_HOME

# --- Importar constructores de Vistas ---
from plantilla import build_solicitudes_view, fill_data_table, _data_table_instance # Importar función de refresco y tabla
from solicitud import build_solicitud_form_view

# --- Importar funciones de Base de Datos (para inicialización) ---
from database import create_connection, create_table

# --- Modelo de Datos de Usuario (Temporal) ---
# Considera mover esto a un lugar más seguro o usar un sistema de autenticación real
users = {
    "operador1": {"password": "pass1", "role": "operador"},
    "admin1": {"password": "adminpass", "role": "administrador"},
    # Puedes añadir más usuarios aquí
}

# --- Estado Global Simple (para referencias a controles principales) ---
# En una app más grande, considera usar una clase App o un gestor de estado
view_container = ft.Container(expand=True, padding=ft.padding.all(15)) # Contenedor donde se mostrarán las vistas
solicitudes_list_view = None # Referencia a la vista de lista (se construye después del login)
solicitud_form_view = None # Referencia a la vista de formulario (se construye después del login)
settings_view = None # Placeholder para la vista de configuración

# --- Funciones de Autenticación ---
def authenticate(username, password):
    """Verifica si el usuario y la contraseña son correctos."""
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None

# --- Función de Cambio de Vista ---
def change_view(page: ft.Page, index: int):
    """
    Cambia la vista mostrada en el contenedor principal basado en el índice.
    """
    global view_container, solicitudes_list_view, solicitud_form_view, settings_view

    print(f"Cambiando a vista índice: {index}") # Para depuración

    view_container.content = None # Limpiar contenido anterior explícitamente
    #view_container.controls.clear() # Limpiar controles por si acaso

    if index == VIEW_HOME: # 0
        # Si Home es igual a la lista, mostrar la lista
        if solicitudes_list_view:
            # Refrescar datos de la tabla al volver a esta vista
            if _data_table_instance:
                 fill_data_table(page, _data_table_instance)
            view_container.content = solicitudes_list_view
        else:
            view_container.content = ft.Text("Error: Vista Home no construida")
    elif index == VIEW_SOLICITUDES_LIST: # 1
        if solicitudes_list_view:
            # Refrescar datos de la tabla al volver a esta vista
            if _data_table_instance:
                 fill_data_table(page, _data_table_instance)
            view_container.content = solicitudes_list_view
        else:
            view_container.content = ft.Text("Error: Vista Lista Solicitudes no construida")
    elif index == VIEW_ADD_SOLICITUD: # 99 (Botón Add)
        if solicitud_form_view:
            view_container.content = solicitud_form_view
            # Opcional: Limpiar el formulario cada vez que se muestra
            # find_control(solicitud_form_view, "clear_button").invoke_handler() # Necesitaría adaptar solicitud.py para exponer/llamar clear_form
        else:
            view_container.content = ft.Text("Error: Vista Formulario Solicitud no construida")
    elif index == VIEW_SETTINGS: # 2
        if settings_view:
            view_container.content = settings_view
        else:
            # Crear una vista placeholder si no existe
            settings_view = ft.Column([ft.Text("Vista de Configuración (Pendiente)", size=20)])
            view_container.content = settings_view
    else:
        view_container.content = ft.Text(f"Vista desconocida: {index}")

    view_container.update() # Actualizar el contenedor
    # page.update() # No siempre necesario si solo actualizas el contenedor

# --- Construcción de la Interfaz Principal (Post-Login) ---
def build_main_app_view(page: ft.Page):
    """Construye y muestra la interfaz principal de la aplicación."""
    global view_container, solicitudes_list_view, solicitud_form_view, settings_view

    print("Construyendo vista principal de la aplicación...")

    # 1. Limpiar la vista de login
    page.clean()
    page.title = "Sistema de Ayudas Sociales" # Cambiar título
    # Resetear alineación y padding si es necesario
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.padding = 0 # El padding se maneja dentro de los contenedores
    page.window_width = 1024 # Ajustar tamaño de ventana
    page.window_height = 768

    # 2. Construir las vistas principales (hacerlo una vez)
    # Asegurarse de que las funciones devuelven el control raíz de su vista
    if not solicitudes_list_view:
        solicitudes_list_view = build_solicitudes_view(page)
    if not solicitud_form_view:
        solicitud_form_view = build_solicitud_form_view(page)
    # settings_view se crea bajo demanda en change_view o puedes crearlo aquí

    # 3. Construir componentes persistentes (AppBar, NavigationRail)
    app_bar = build_app_bar()
    # Pasar la función de cambio de vista al NavigationRail
    navigation_rail = build_navigation_rail(lambda idx: change_view(page, idx))

    # 4. Configurar el Layout Principal
    page.appbar = app_bar
    page.add(
        ft.Row(
            [
                navigation_rail,
                ft.VerticalDivider(width=1),
                view_container, # El contenedor donde irán las vistas dinámicas
            ],
            expand=True, # La fila ocupa todo el espacio
        )
    )

    # 5. Mostrar la vista inicial por defecto
    change_view(page, VIEW_SOLICITUDES_LIST) # Empezar mostrando la lista

    page.update()
    print("Vista principal construida y mostrada.")

# --- Construcción de la Interfaz de Login ---
def build_login_view(page: ft.Page, on_login_success):
    """Construye y muestra la interfaz de login."""
    page.title = "Ayudas Sociales - Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 350 # Un poco más de espacio
    page.padding = 20

    welcome_message = ft.Text("Bienvenido al Sistema", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    username_field = ft.TextField(label="Usuario", width=300, autofocus=True)
    password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, on_submit=lambda e: login_clicked(e)) # Permitir login con Enter
    login_button = ft.ElevatedButton(text="Iniciar Sesión", width=300)
    error_message = ft.Text("", color=ft.colors.RED, text_align=ft.TextAlign.CENTER)

    def login_clicked(e):
        """Maneja el evento de clic en el botón de Iniciar Sesión."""
        username = username_field.value.strip()
        password = password_field.value
        role = authenticate(username, password)

        if role:
            print(f"Autenticación exitosa para {username} con rol {role}")
            error_message.value = ""
            error_message.update()
            # Llamar a la función que construye la vista principal
            on_login_success(page)
        else:
            print(f"Autenticación fallida para {username}")
            error_message.value = "Usuario o contraseña incorrectos"
            error_message.update()
            password_field.value = "" # Limpiar contraseña
            password_field.focus() # Poner foco en contraseña
            password_field.update()


    login_button.on_click = login_clicked

    page.add(
        ft.Column(
            [
                welcome_message,
                ft.Divider(height=20, color="transparent"),
                username_field,
                password_field,
                ft.Divider(height=10, color="transparent"),
                login_button,
                error_message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, # Centrar verticalmente la columna
            spacing=15,
            expand=True # Hacer que la columna ocupe el espacio vertical
        )
    )
    page.update()

# --- Punto de Entrada Principal ---
def main(page: ft.Page):
    # Mostrar la vista de login inicialmente, pasando la función
    # que debe ejecutarse si el login es exitoso.
    build_login_view(page, build_main_app_view)

# --- Ejecución de la Aplicación ---
if __name__ == "__main__":
    # Asegurar que la base de datos y las tablas existan antes de iniciar
    print("Verificando base de datos...")
    conn = create_connection()
    if conn:
        create_table(conn)
        conn.close()
        print("Base de datos lista.")
    else:
        print("¡ERROR CRÍTICO! No se pudo conectar/crear la base de datos.")
        # Podrías decidir no iniciar la app aquí si la DB es esencial

    # Iniciar la aplicación Flet
    ft.app(target=main)
