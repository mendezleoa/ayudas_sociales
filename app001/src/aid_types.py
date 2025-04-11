# c:\Users\lmendez\Desktop\Desarrollo en Flet\ayudas_sociales\app001\src\aid_types.py
import flet as ft

# Importamos UserControl directamente para la herencia
from flet.core.control import Control as UserControl
from database import (
    create_connection,
    create_table,
    add_aid_type,
    get_all_aid_types,
    update_aid_type,
    delete_aid_type,
)

class AidTypesView(UserControl):
    """
    Vista de Flet para gestionar (CRUD) los Tipos de Ayuda.
    """
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Almacena el ID del tipo seleccionado para editar, None si se está creando uno nuevo
        self._selected_aid_type_id = None

        # --- Controles del Formulario ---
        self.name_field = ft.TextField(
            label="Nombre del tipo de ayuda*",
            expand=True,
            on_change=self._clear_field_error # Limpiar error al escribir
        )
        self.description_field = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True
        )
        self.save_button = ft.ElevatedButton(
            "Guardar",
            icon=ft.icons.SAVE_OUTLINED,
            on_click=self._save_button_click,
            # Estilo opcional para bordes redondeados
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        self.clear_button = ft.OutlinedButton(
            "Limpiar",
            icon=ft.icons.CLEAR_ALL_OUTLINED,
            on_click=self._clear_form,
            # Estilo opcional para bordes redondeados
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        # Texto para mostrar errores generales del formulario (ej. duplicados)
        self.form_error_text = ft.Text("", color=ft.colors.RED_500, visible=False)

        # --- Lista/Tabla de Tipos de Ayuda ---
        self.aid_types_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD), numeric=True), # numeric=True alinea a la derecha
            ],
            rows=[], # Las filas se llenarán dinámicamente
            expand=True, # Para que la tabla ocupe el espacio disponible
            # Estilos opcionales para la tabla
            border=ft.border.all(1, ft.colors.BLACK26),
            border_radius=ft.border_radius.all(8),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
            column_spacing=20, # Espacio entre columnas
        )

        # --- Diálogo de Confirmación para Eliminar ---
        self.confirm_delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro de que quieres eliminar este tipo de ayuda? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Sí, Eliminar", on_click=self._confirm_delete, style=ft.ButtonStyle(color=ft.colors.RED)),
                ft.TextButton("No, Cancelar", on_click=self._close_delete_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # Variable para guardar temporalmente el ID a eliminar
        self._aid_type_to_delete_id = None

    def build(self):
        """
        Construye la interfaz gráfica de la vista.
        """
        # Cargar los datos iniciales en la tabla al construir la vista
        self._load_aid_types()

        return ft.Column(
            expand=True, # Ocupa el espacio vertical disponible
            controls=[
                ft.Text("Gestión de Tipos de Ayuda", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"), # Pequeño espacio

                # --- Sección del Formulario ---
                ft.Container(
                    padding=ft.padding.all(15),
                    border=ft.border.all(1, ft.colors.BLACK12), # Borde sutil
                    border_radius=ft.border_radius.all(8),
                    content=ft.Column([
                        ft.Row([self.name_field]), # Nombre en una fila
                        ft.Row([self.description_field]), # Descripción en otra fila
                        self.form_error_text, # Espacio para errores del formulario
                        ft.Row(
                            [self.save_button, self.clear_button],
                            alignment=ft.MainAxisAlignment.END # Botones a la derecha
                        )
                    ]),
                ),

                ft.Divider(height=20), # Espacio mayor

                # --- Sección de la Lista/Tabla ---
                ft.Text("Tipos de ayuda existentes:", size=18),
                ft.Container(
                    expand=True, # Permitir que la tabla ocupe el espacio restante
                    content=ft.Column( # Usar Column para permitir scroll si es necesario
                        scroll=ft.ScrollMode.ADAPTIVE, # Scroll si el contenido excede
                        expand=True,
                        controls=[self.aid_types_table] # La tabla dentro de la columna scrollable
                    )
                )
            ]
        )

    # --- Métodos Auxiliares y Handlers ---

    def _show_snackbar(self, message, color=ft.colors.GREEN_200, duration=3000):
        """Muestra un SnackBar con un mensaje."""
        if self.page: # Asegurarse de que la página esté disponible
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text(message),
                    bgcolor=color,
                    duration=duration
                )
            )

    def _clear_field_error(self, e):
        """Limpia el error del campo de nombre al escribir."""
        if e.control == self.name_field:
            self.name_field.error_text = None
        # Ocultar también el error general del formulario
        self.form_error_text.value = ""
        self.form_error_text.visible = False
        self.update()

    def _clear_form(self, e=None):
        """Limpia los campos del formulario y resetea el estado de edición."""
        self._selected_aid_type_id = None # Resetear ID seleccionado
        self.name_field.value = ""
        self.description_field.value = ""
        self.name_field.error_text = None # Limpiar posible error
        self.form_error_text.value = "" # Limpiar error general
        self.form_error_text.visible = False
        self.save_button.text = "Guardar" # Restaurar texto del botón
        print("Formulario limpiado.")
        self.update() # Actualizar la UI

    def _load_aid_types(self):
        """Carga los tipos de ayuda desde la DB y actualiza la tabla."""
        print("Cargando tipos de ayuda desde la base de datos...")
        conn = None
        try:
            conn = create_connection()
            if not conn:
                self._show_snackbar("Error: No se pudo conectar a la base de datos.", ft.colors.RED_200)
                self.aid_types_table.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text("Error de conexión", color="red"), colspan=3)])]
                self.update()
                return

            aid_types_data = get_all_aid_types(conn) # Obtener datos
            self.aid_types_table.rows.clear() # Limpiar filas actuales

            if not aid_types_data:
                # Mostrar mensaje si no hay datos
                self.aid_types_table.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text("No hay tipos de ayuda registrados.", italic=True), colspan=3)])
                )
            else:
                # Crear filas para cada tipo de ayuda
                for aid_id, nombre, descripcion in aid_types_data:
                    self.aid_types_table.rows.append(
                        ft.DataRow(
                            # Guardamos el ID en el atributo 'data' de la fila para fácil acceso
                            data={'id': aid_id, 'nombre': nombre, 'descripcion': descripcion},
                            cells=[
                                ft.DataCell(ft.Text(nombre)),
                                ft.DataCell(ft.Text(descripcion or "-")), # Mostrar '-' si la descripción es None o vacía
                                ft.DataCell(
                                    # Fila con botones de acción
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.icons.EDIT_OUTLINED,
                                            tooltip="Editar",
                                            # Pasamos el ID y datos a la función de editar
                                            on_click=lambda _, r=self.aid_types_table.rows[-1]: self._edit_aid_type(r.data['id'], r.data['nombre'], r.data['descripcion']),
                                            icon_color=ft.colors.BLUE_600
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINE,
                                            tooltip="Eliminar",
                                            # Pasamos el ID a la función de eliminar
                                            on_click=lambda _, r=self.aid_types_table.rows[-1]: self._delete_aid_type_click(r.data['id']),
                                            icon_color=ft.colors.RED_600
                                        ),
                                    ], spacing=0) # spacing=0 para juntar los iconos
                                ),
                            ]
                        )
                    )
            print(f"Tipos de ayuda cargados en la tabla: {len(aid_types_data)}")

        except Exception as e:
            print(f"Error inesperado al cargar tipos de ayuda: {e}")
            self._show_snackbar(f"Error al cargar datos: {e}", ft.colors.RED_200)
            # Mostrar mensaje de error en la tabla
            self.aid_types_table.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(f"Error al cargar: {e}", color="red"), colspan=3)])]
        finally:
            if conn:
                conn.close()
                print("Conexión cerrada después de cargar tipos.")

        self.update() # Actualizar la interfaz para mostrar los cambios en la tabla

    def _edit_aid_type(self, aid_id, nombre, descripcion):
        """Prepara el formulario para editar un tipo de ayuda existente."""
        print(f"Editando tipo ID: {aid_id}, Nombre: {nombre}")
        self._selected_aid_type_id = aid_id # Guardar el ID que estamos editando
        self.name_field.value = nombre
        self.description_field.value = descripcion or "" # Usar "" si es None
        self.name_field.error_text = None # Limpiar errores previos
        self.form_error_text.value = ""
        self.form_error_text.visible = False
        self.save_button.text = "Actualizar" # Cambiar texto del botón
        self.name_field.focus() # Poner foco en el campo nombre para facilitar edición
        self.update()

    def _save_button_click(self, e):
        """Maneja el clic en el botón Guardar/Actualizar."""
        nombre = self.name_field.value.strip() # Quitar espacios extra
        descripcion = self.description_field.value.strip()

        # Validación simple: Nombre es requerido
        if not nombre:
            self.name_field.error_text = "El nombre es requerido"
            self.update()
            return

        conn = None
        success = False
        try:
            conn = create_connection()
            if not conn:
                self._show_snackbar("Error: No se pudo conectar a la base de datos.", ft.colors.RED_200)
                return

            if self._selected_aid_type_id:
                # --- Modo Actualizar ---
                print(f"Intentando actualizar tipo ID: {self._selected_aid_type_id} con nombre: {nombre}")
                success = update_aid_type(conn, self._selected_aid_type_id, nombre, descripcion)
                if success:
                    self._show_snackbar("Tipo de ayuda actualizado correctamente.")
                else:
                    # update_aid_type ya imprime el error de duplicado o no encontrado
                    # Mostramos un error genérico en el formulario si no fue por duplicado
                    # (Podríamos verificar el error específico si la función lo devolviera)
                    self.form_error_text.value = "Error al actualizar. ¿El nombre ya existe o el ID es inválido?"
                    self.form_error_text.visible = True
                    self.update()
                    # No limpiar formulario si hay error para que el usuario corrija

            else:
                # --- Modo Crear ---
                print(f"Intentando crear nuevo tipo con nombre: {nombre}")
                new_id = add_aid_type(conn, nombre, descripcion)
                if new_id:
                    success = True
                    self._show_snackbar("Tipo de ayuda creado correctamente.")
                else:
                    # add_aid_type ya imprime el error de duplicado
                    self.form_error_text.value = "Error al crear. ¿El nombre ya existe?"
                    self.form_error_text.visible = True
                    self.update()
                    # No limpiar formulario si hay error

            # Si la operación (crear o actualizar) fue exitosa:
            if success:
                self._clear_form() # Limpiar el formulario
                self._load_aid_types() # Recargar la lista/tabla

        except Exception as ex:
            print(f"Error inesperado en operación de guardado: {ex}")
            self._show_snackbar(f"Error inesperado: {ex}", ft.colors.RED_200)
            self.form_error_text.value = f"Error inesperado: {ex}"
            self.form_error_text.visible = True
            self.update()
        finally:
            if conn:
                conn.close()
                print("Conexión cerrada después de guardar/actualizar.")

    def _delete_aid_type_click(self, aid_id):
        """Muestra el diálogo de confirmación antes de eliminar."""
        print(f"Click en eliminar para ID: {aid_id}")
        self._aid_type_to_delete_id = aid_id # Guardar el ID a eliminar
        self.page.dialog = self.confirm_delete_dialog # Asignar el diálogo a la página
        self.confirm_delete_dialog.open = True # Abrir el diálogo
        self.page.update() # Actualizar la página para mostrar el diálogo

    def _close_delete_dialog(self, e):
        """Cierra el diálogo de confirmación sin eliminar."""
        print("Cancelada eliminación.")
        self.confirm_delete_dialog.open = False
        self._aid_type_to_delete_id = None # Limpiar ID guardado
        self.page.update()

    def _confirm_delete(self, e):
        """Confirma y ejecuta la eliminación del tipo de ayuda."""
        aid_id = self._aid_type_to_delete_id
        print(f"Confirmada eliminación para ID: {aid_id}")
        self.confirm_delete_dialog.open = False # Cerrar diálogo primero
        self.page.update() # Actualizar UI para cerrar diálogo

        if not aid_id:
            print("Error: No hay ID para eliminar.")
            return

        conn = None
        success = False
        try:
            conn = create_connection()
            if not conn:
                self._show_snackbar("Error: No se pudo conectar a la base de datos.", ft.colors.RED_200)
                return

            success = delete_aid_type(conn, aid_id)

            if success:
                self._show_snackbar("Tipo de ayuda eliminado correctamente.")
                self._load_aid_types() # Recargar la lista para reflejar la eliminación
            else:
                # delete_aid_type ya imprime si no se encontró el ID
                self._show_snackbar("Error al eliminar el tipo de ayuda.", ft.colors.RED_200)

        except Exception as ex:
            print(f"Error inesperado al eliminar: {ex}")
            self._show_snackbar(f"Error inesperado al eliminar: {ex}", ft.colors.RED_200)
        finally:
            if conn:
                conn.close()
                print("Conexión cerrada después de eliminar.")
            self._aid_type_to_delete_id = None # Limpiar ID a eliminar en cualquier caso

    # Método público para permitir refrescar desde fuera (ej. al cambiar a esta vista)
    def refresh_data(self):
        """Recarga los datos de la tabla."""
        print("Refrescando datos de AidTypesView...")
        self._load_aid_types()

# --- Bloque de prueba (Opcional) ---
def _test_main(page: ft.Page):
    """Función para probar esta vista de forma aislada."""
    page.title = "Test CRUD Tipos de Ayuda"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH # Estirar contenido horizontalmente

    # Asegurar que la tabla exista para las pruebas
    conn_test = create_connection()
    if conn_test:
        create_table(conn_test)
        conn_test.close()
    else:
        page.add(ft.Text("Error conectando a DB para prueba"))
        return

    # Crear instancia de la vista
    crud_view = AidTypesView(page)

    # Añadir la vista a la página
    page.add(
        ft.Container(
            # Envuelve en un Container para padding si es necesario
            padding=ft.padding.all(20),
            expand=True,
            content=crud_view
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=_test_main)
