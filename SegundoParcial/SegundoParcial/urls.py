from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from gestion import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Ruta para cerrar sesión
    path('bitacora/', views.ver_bitacora, name='ver_bitacora'),
    path('alumno/', views.alumno_panel, name='alumno_panel'),
    path('instructor/', views.instructor_panel, name='instructor_panel'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/credenciales/', views.admin_credenciales, name='admin_credenciales'),
    path('admin_panel/credenciales/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),  # Ruta para editar usuario
    path('admin_panel/credenciales/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),  # Ruta para eliminar usuario
    path('admin_panel/inventario/', views.inventario_view, name='inventario'),
    path('admin_panel/cursos/', views.asignar_cursos, name='asignar_cursos'),
    path('admin_panel/cursos/editar/<int:pk>/', views.editar_curso, name='editar_curso'),
    path('admin_panel/cursos/eliminar/<int:pk>/', views.eliminar_curso, name='eliminar_curso'),
    path('admin_panel/cursos/asignar_profesores/<int:pk>/', views.asignar_profesores, name='asignar_profesores'),
    path('admin_panel/quejas/', views.ver_quejas, name='ver_quejas'),  # Página de visualización de quejas
    path('', lambda request: redirect('login')),  # Redirigir la ruta raíz al login
]
