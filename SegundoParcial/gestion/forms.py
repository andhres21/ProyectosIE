from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import PagoCurso, Curso, Usuario, Inventario, AsignacionInventario, Queja, Reporte, Retroalimentacion

# Definimos las opciones de rol
ROL_CHOICES = [
    ('admin', 'Administrador'),
    ('instructor', 'Instructor'),
    ('alumno', 'Alumno')
]

class CrearUsuarioForm(UserCreationForm):
    rol = forms.ChoiceField(choices=ROL_CHOICES, label='Rol')  # Añadimos el campo de rol

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')

        # Asigna el rol basado en la elección
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

        # Guardar el usuario con la contraseña encriptada
        if commit:
            user.set_password(self.cleaned_data["password1"])
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
        fields = ['nombre', 'descripcion', 'cupo_maximo', 'horario', 'costo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. Salsa, Bachata'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Descripción breve del curso'
            }),
            'cupo_maximo': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1'
            }),
            'horario': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. 10:00 - 11:00'
            }),
            'costo': forms.NumberInput(attrs={  # Cambiado a NumberInput
                'class': 'form-control', 
                'placeholder': 'Ej. 20.00',
                'min': '0',
                'step': '0.01'
            }),
        }



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

class AsignarInventarioForm(forms.ModelForm):
    cantidad_asignada = forms.IntegerField(min_value=1, label="Cantidad a asignar")

    class Meta:
        model = AsignacionInventario
        fields = ['usuario', 'inventario', 'cantidad_asignada']
        labels = {
            'usuario': 'Instructor',
            'inventario': 'Artículo de Inventario',
        }

class QuejaForm(forms.ModelForm):
    class Meta:
        model = Queja
        fields = ['asunto', 'descripcion']
        labels = {
            'asunto': 'Asunto',
            'descripcion': 'Queja',
        }

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['asunto', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class RetroalimentacionForm(forms.ModelForm):
    class Meta:
        model = Retroalimentacion
        fields = ['alumno', 'curso', 'mensaje']

    def __init__(self, *args, **kwargs):
        instructor = kwargs.pop('instructor', None)  # Extraer el instructor del argumento
        super().__init__(*args, **kwargs)
        
        if instructor:
            # Filtrar cursos solo a los impartidos por el instructor logueado
            cursos_instructor = Curso.objects.filter(instructor=instructor)
            self.fields['curso'].queryset = Curso.objects.all()

            # Filtrar alumnos solo a los inscritos en los cursos del instructor y que sean "alumnos"
            self.fields['alumno'].queryset = Usuario.objects.filter(is_alumno=True)

class PagoCursoForm(forms.ModelForm):
    class Meta:
        model = PagoCurso
        fields = []  # No incluimos 'curso' ni 'monto_pagado' ya que se establecerán automáticamente

    def __init__(self, *args, **kwargs):
        self.curso = kwargs.pop('curso', None)  # Se recibe el curso como argumento
        self.student = kwargs.pop('student', None)  # Se recibe el estudiante como argumento
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        pago = super().save(commit=False)
        if self.student:
            pago.alumno = self.student  # Asigna el estudiante
        if self.curso:
            pago.curso = self.curso  # Asigna el curso
            pago.monto_pagado = self.curso.costo  # Asigna el costo del curso como monto pagado
        if commit:
            pago.save()
        return pago

