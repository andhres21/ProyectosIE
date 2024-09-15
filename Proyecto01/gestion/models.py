from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('profesor', 'Catedrático'),
        ('estudiante', 'Estudiante'),
    ]
    role = models.CharField(max_length=10, choices=ROLES)  # Campo para los roles

    # Añade related_name para evitar conflictos con el modelo User de Django
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    cupo = models.IntegerField()
    
    # Añade related_name para evitar conflictos
    catedratico = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'profesor'},
        related_name='cursos_catedratico'
    )
    estudiantes = models.ManyToManyField(
        Usuario, 
        limit_choices_to={'role': 'estudiante'},
        related_name='cursos_estudiantes'
    )

class Nota(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'role': 'estudiante'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    nota = models.FloatField(null=True, blank=True)  # Permite valores nulos para la nota inicialmente

