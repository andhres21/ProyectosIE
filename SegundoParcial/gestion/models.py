from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model



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
    horario = models.CharField(max_length=100, null=False)
    cupo_maximo = models.IntegerField(default=0)
    cupo_ocupado = models.IntegerField(default=0)
    instructor = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    alumnos = models.ManyToManyField(Usuario, related_name="cursos", blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Campo de costo

    def __str__(self):
        return f"{self.nombre} - ${self.costo}"  # Opcional: Muestra el costo en el string
    
    def pago_realizado_por(self, alumno):
        """Verifica si el alumno ha realizado el pago para este curso."""
        return self.pago_curso_set.filter(alumno=alumno).exists()

Usuario = get_user_model()
class AsignacionCurso(models.Model):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)  # Relación con el curso
    instructor = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)  # Instructor asignado
    seccion = models.CharField(max_length=1, choices=[('A', 'Sección A'), ('B', 'Sección B'), ('C', 'Sección C')])  # Sección del curso
    alumnos = models.ManyToManyField(Usuario, related_name='cursos_asignados', blank=True)  # Alumnos asignados
    cupo_maximo = models.IntegerField(default=0)  # Cupo máximo
    cupo_ocupado = models.IntegerField(default=0)  # Cupo ocupado

    def save(self, *args, **kwargs):
        # Si el cupo_maximo no está asignado, usar el cupo_maximo del curso
        if self.cupo_maximo == 0:
            self.cupo_maximo = self.curso.cupo_maximo
        super(AsignacionCurso, self).save(*args, **kwargs)

    def cupo_disponible(self):
        return self.cupo_maximo - self.cupo_ocupado

    def asignar_alumno(self, alumno):
        if self.cupo_ocupado < self.cupo_maximo:
            self.alumnos.add(alumno)
            self.cupo_ocupado += 1
            self.save()
            return True
        return False

    def desasignar_alumno(self, alumno):
        if alumno in self.alumnos.all():
            self.alumnos.remove(alumno)
            self.cupo_ocupado -= 1
            self.save()
            return True
        return False


class Inventario(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_total = models.IntegerField(default=0)
    cantidad_disponible = models.IntegerField(default=0)
    cantidad_prestada = models.IntegerField(default=0)
    
    # Asegúrate de tener un campo para asignar el inventario a un usuario (instructor).
    asignado_a = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)  # Usuario que recibe el inventario

    def save(self, *args, **kwargs):
        # Asegurar que la cantidad disponible se calcule correctamente
        self.cantidad_disponible = self.cantidad_total - self.cantidad_prestada
        super(Inventario, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class AsignacionInventario(models.Model):
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'is_instructor': True})
    cantidad_asignada = models.IntegerField()
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)  # Esto es para la devolución de artículos

    def __str__(self):
        return f"{self.usuario.username} - {self.inventario.nombre} - {self.cantidad_asignada}"

class Bitacora(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # El usuario que realiza la acción
    accion = models.CharField(max_length=255)  # Descripción de la acción
    fecha_hora = models.DateTimeField(default=timezone.now)  # Fecha y hora de la acción

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha_hora}"

Usuario = get_user_model()

class Queja(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relacionar al alumno que hizo la queja
    asunto = models.CharField(max_length=255)  # Asunto de la queja
    descripcion = models.TextField()  # Texto de la queja
    fecha = models.DateTimeField(default=timezone.now)  # Fecha y hora de la queja

    def __str__(self):
        return f"{self.asunto} - {self.alumno.username}"
    
class Reporte(models.Model):
    instructor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes_enviados')
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte de {self.instructor.username} - {self.asunto}"


class Retroalimentacion(models.Model):
    instructor = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='retroalimentaciones_enviadas'  # Nombre único para la relación inversa
    )
    alumno = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='retroalimentaciones_recibidas'  # Nombre único para la relación inversa
    )
    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True)  # Permitir valores nulos
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Retroalimentación de {self.instructor.username} a {self.alumno.username} en el curso {self.curso.nombre}"

class PagoCurso(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.alumno.username} por el curso {self.curso.nombre} - ${self.monto_pagado}"