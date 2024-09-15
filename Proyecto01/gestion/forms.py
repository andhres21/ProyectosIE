from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from .models import Curso, Usuario

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'role']  # Agrega los campos que desees mostrar

class ProfesorCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        # Establecer el rol de profesor automáticamente
        user = super().save(commit=False)
        user.role = 'profesor'
        if commit:
            user.save()
        return user

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'cupo', 'catedratico']

    # Filtro para mostrar solo profesores en la selección de catedrático
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['catedratico'].queryset = Usuario.objects.filter(role='profesor')
