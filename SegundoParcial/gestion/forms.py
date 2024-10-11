from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Curso, Usuario, Inventario

# Definimos las opciones de rol
ROL_CHOICES = [
    ('admin', 'Administrador'),
    ('instructor', 'Instructor'),
    ('alumno', 'Alumno'),
]

class CrearUsuarioForm(UserCreationForm):
    rol = forms.ChoiceField(choices=ROL_CHOICES, label='Rol')  # Añadimos el campo de rol

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        # Sobrescribimos el método save para que asigne el rol seleccionado
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')
        if rol == 'admin':
            user.is_admin = True
            user.is_instructor = False
            user.is_alumno = False
        elif rol == 'instructor':
            user.is_admin = False
            user.is_instructor = True
            user.is_alumno = False
        elif rol == 'alumno':
            user.is_admin = False
            user.is_instructor = False
            user.is_alumno = True
        if commit:
            user.save()
        return user

class EditarUsuarioForm(UserChangeForm):
    rol = forms.ChoiceField(choices=ROL_CHOICES, label='Rol', initial='alumno')

    class Meta:
        model = Usuario
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')
        if rol == 'admin':
            user.is_admin = True
            user.is_instructor = False
            user.is_alumno = False
        elif rol == 'instructor':
            user.is_admin = False
            user.is_instructor = True
            user.is_alumno = False
        elif rol == 'alumno':
            user.is_admin = False
            user.is_instructor = False
            user.is_alumno = True
        if commit:
            user.save()
        return user

class CrearCursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'seccion_horario', 'cupo']

class AsignarProfesoresForm(forms.ModelForm):
    profesores = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(is_instructor=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Curso
        fields = ['profesores']

class CrearInventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['nombre', 'cantidad_total']
        labels = {
            'nombre': 'Nombre del producto',
            'cantidad_total': 'Cantidad inicial',
        }