import flet as ft

# --- Modelo de Datos de Usuario (Temporal) ---
users = {
    "operador1": {"password": "pass1", "role": "operador"},
    "admin1": {"password": "adminpass", "role": "administrador"},
}

# --- Funciones de Autenticación ---
def authenticate(username, password):
    """Verifica si el usuario y la contraseña son correctos."""
    if username in users and users[username]["password"] == password:
        return users[username]["role"]
    return None

# --- Funciones de Navegación ---
def show_operator_view(page):
    """Muestra la vista del operador."""
    page.clean()
    page.add(ft.Text("Bienvenido, Operador", size=30))
    page.update()

def show_admin_view(page):
    """Muestra la vista del administrador."""
    page.clean()
    page.add(ft.Text("Bienvenido, Administrador", size=30))
    page.update()

# --- Interfaz de Login ---
def main(page: ft.Page):
    page.title = "Ayudas Sociales - Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 300

    # Mensaje de Bienvenida
    welcome_message = ft.Text("Bienvenido al Sistema de Ayudas Sociales", size=20, weight=ft.FontWeight.BOLD)

    username_field = ft.TextField(label="Usuario", width=300)
    password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    login_button = ft.ElevatedButton(text="Iniciar Sesión", width=300)
    error_message = ft.Text("", color=ft.Colors.RED)

    def login_clicked(e):
        """Maneja el evento de clic en el botón de Iniciar Sesión."""
        role = authenticate(username_field.value, password_field.value)
        if role:
            error_message.value = ""
            if role == "operador":
                show_operator_view(page)
            elif role == "administrador":
                show_admin_view(page)
        else:
            error_message.value = "Usuario o contraseña incorrectos"
        page.update()

    login_button.on_click = login_clicked

    page.add(
        ft.Column(
            [
                welcome_message,
                username_field,
                password_field,
                login_button,
                error_message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )

ft.app(target=main)
