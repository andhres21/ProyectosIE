from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario  # Asegúrate de que esté importado tu modelo extendido

class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista de usuarios en el admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    
    # Campos que serán editables en el formulario de usuarios
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
        ('Rol', {'fields': ('role',)}),  # Asegúrate de incluir el campo `role` aquí
    )

# Registrar el modelo Usuario en el panel de administración
admin.site.register(Usuario, UsuarioAdmin)
