from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    is_alumno = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',  # Evitar conflictos con el modelo auth.User
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permission_set',  # Evitar conflictos con el modelo auth.User
        blank=True
    )

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    seccion_horario = models.CharField(max_length=100)
    cupo = models.IntegerField(default=20)
    # Se usa AsignacionCurso para relacionar el curso con los profesores
    profesores = models.ManyToManyField(Usuario, through='AsignacionCurso', related_name='cursos')

    def __str__(self):
        return self.nombre

class AsignacionCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)  # Permitir que sea nulo
    seccion = models.CharField(max_length=1, choices=[('A', 'Sección A'), ('B', 'Sección B'), ('C', 'Sección C')])

    def __str__(self):
        if self.profesor:
            return f"{self.profesor.username} en {self.seccion} para el curso {self.curso.nombre}"
        else:
            return f"Sin asignar en {self.seccion} para el curso {self.curso.nombre}"

class Inventario(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_total = models.IntegerField(default=0)
    cantidad_disponible = models.IntegerField(default=0)
    cantidad_prestada = models.IntegerField(default=0)

def save(self, *args, **kwargs):
    # Asegurar que los valores no sean None antes de convertirlos
    self.cantidad_total = int(self.cantidad_total) if self.cantidad_total is not None else 0
    self.cantidad_prestada = int(self.cantidad_prestada) if self.cantidad_prestada is not None else 0

    # Realizar la operación para calcular la cantidad disponible
    self.cantidad_disponible = self.cantidad_total - self.cantidad_prestada

    # Llamar al método save de la clase padre
    super(Inventario, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Bitacora(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # El usuario que realiza la acción
    accion = models.CharField(max_length=255)  # Descripción de la acción
    fecha_hora = models.DateTimeField(default=timezone.now)  # Fecha y hora de la acción

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha_hora}"
