# src/validators.py
import flet as ft
import re

def validate_required(control: ft.Control, field_name="Este campo"):
    """Valida que un campo (TextField, Dropdown) no esté vacío."""
    # Asegurarse de que el control tenga la propiedad 'value'
    if not hasattr(control, 'value') or not control.value:
        control.error_text = f"{field_name} es requerido"
        if hasattr(control, 'update'):
            control.update()
        return False
    control.error_text = None
    if hasattr(control, 'update'):
        control.update()
    return True

def validate_phone(control: ft.TextField):
    """Valida que el teléfono tenga un formato simple (ej. >= 7 dígitos)."""
    if not control.value:
        control.error_text = "El teléfono es requerido"
        control.update()
        return False
    # Simplificamos la validación a solo dígitos y longitud mínima
    phone_pattern = r"^\d{7,}$"
    if not re.match(phone_pattern, control.value):
        control.error_text = "Formato de teléfono inválido (solo números, mín 7 dígitos)"
        control.update()
        return False
    control.error_text = None
    control.update()
    return True

def validate_email(control: ft.TextField):
    """Valida que el correo electrónico tenga un formato correcto."""
    # Si el campo está vacío y no es requerido, es válido (ajustar si el email es siempre requerido)
    if not control.value:
        control.error_text = None
        control.update()
        return True
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, control.value):
        control.error_text = "Formato de correo electrónico incorrecto"
        control.update()
        return False
    control.error_text = None
    control.update()
    return True

def validate_numeric(control: ft.TextField, field_name="Este campo"):
    """Valida que el campo contenga un número entero positivo."""
    if not control.value:
        control.error_text = f"{field_name} es requerido"
        control.update()
        return False
    if not control.value.isdigit() or int(control.value) <= 0:
        control.error_text = f"{field_name} debe ser un número positivo"
        control.update()
        return False
    control.error_text = None
    control.update()
    return True

# Puedes añadir más validadores aquí (ej. fecha, longitud específica, etc.)
