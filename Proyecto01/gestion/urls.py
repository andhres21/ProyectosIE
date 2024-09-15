from django.urls import path
from gestion import views
from django.contrib.auth import views as auth_views

# Rutas para la aplicación "gestion"
urlpatterns = [
    # Rutas de autenticación y páginas de inicio
    path('', views.home, name='home'),  # Ruta para la página de inicio
    path('registro/', views.registro, name='registro'),  # Ruta para el registro
    path('dashboard/', views.dashboard, name='dashboard'),  # Ruta del dashboard general
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Dashboard del administrador
    path('profesor_dashboard/', views.profesor_dashboard, name='profesor_dashboard'),  # Dashboard del catedrático
    path('estudiante_dashboard/', views.estudiante_dashboard, name='estudiante_dashboard'),  # Dashboard del estudiante

    # Rutas para la recuperación de contraseñas
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Rutas para la gestión de profesores y cursos
    path('agregar_profesor/', views.agregar_profesor, name='agregar_profesor'),  # Agregar profesor
    path('lista_profesores/', views.lista_profesores, name='lista_profesores'),  # Listar profesores
    path('agregar_curso/', views.agregar_curso, name='agregar_curso'),  # Agregar curso
    path('lista_cursos/', views.lista_cursos, name='lista_cursos'),  # Listar cursos

    # Rutas para la vista de estudiantes
    path('asignarse_curso/<int:curso_id>/', views.asignarse_curso, name='asignarse_curso'),
    path('cursos/', views.lista_cursos_estudiante, name='lista_cursos_estudiante'),  # Lista de cursos para estudiantes
    path('inscribirse/<int:curso_id>/', views.inscribirse_curso, name='inscribirse_curso'),  # Ruta para inscribirse en curso

    path('profesor/curso/', views.profesor_cursos, name='profesor_cursos'),  # Ver los cursos que imparte el profesor
    path('profesor/curso/<int:curso_id>/estudiantes/', views.profesor_estudiantes, name='profesor_estudiantes'),  # Ver estudiantes en un curso
    path('profesor/curso/<int:curso_id>/estudiante/<int:estudiante_id>/nota/', views.profesor_asignar_nota, name='profesor_asignar_nota'),  # Asignar/modificar nota
]
