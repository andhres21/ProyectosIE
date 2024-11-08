from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from gestion import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ver_pagos/', views.ver_pagos, name='ver_pagos'),
    path('ver_contabilidad/', views.ver_contabilidad, name='ver_contabilidad'),
    path('pago_curso/<int:curso_id>/', views.pago_curso, name='pago_curso'),  # Añade esta línea
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Ruta para cerrar sesión
    path('bitacora/', views.ver_bitacora, name='ver_bitacora'),
    path('bitacora/borrar/', views.borrar_historial, name='borrar_historial'),
    path('alumno/', views.alumno_panel, name='alumno_panel'),
    path('alumno/asignar/<int:curso_id>/', views.asignar_curso_alumno, name='asignar_curso_alumno'),
    path('alumno/desasignar/<int:curso_id>/', views.desasignar_curso_alumno, name='desasignar_curso_alumno'),
    path('alumno/asignar/', views.asignar_cursos_alumno, name='asignar_cursos_alumno'),
    path('alumno/atencion_cliente/', views.atencion_cliente, name='atencion_cliente'),


    path('instructor/', views.instructor_panel, name='instructor_panel'),
    path('instructor/ver_alumnos/', views.ver_alumnos_asignados, name='ver_alumnos_asignados'),
    path('instructor/administrar_inscripciones/', views.administrar_inscripciones, name='administrar_inscripciones'),
    path('instructor/inventario/', views.administrar_inventario, name='administrar_inventario'),
    path('instructor/desasignar_alumno/<int:curso_id>/<int:alumno_id>/', views.desasignar_alumno, name='desasignar_alumno'),
    path('instructor/reporte/', views.enviar_reporte, name='enviar_reporte'),
    path('instructor/retroalimentacion/', views.enviar_retroalimentacion, name='enviar_retroalimentacion'),


    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/credenciales/', views.admin_credenciales, name='admin_credenciales'),
    path('admin_panel/credenciales/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),  # Ruta para editar usuario
    path('admin_panel/credenciales/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),  # Ruta para eliminar usuario
    path('admin_panel/inventario/', views.inventario_view, name='inventario'),
    path('admin_panel/inventario/asignar/', views.asignar_inventario, name='asignar_inventario'),
    path('admin_panel/inventario/devolver/', views.devolver_inventario, name='devolver_inventario'),
    path('admin_panel/inventario/eliminar/<int:pk>/', views.eliminar_inventario, name='eliminar_inventario'),
    path('admin_panel/cursos/', views.asignar_cursos, name='asignar_cursos'),
    path('admin_panel/cursos/editar/<int:pk>/', views.editar_curso, name='editar_curso'),
    path('admin_panel/cursos/eliminar/<int:pk>/', views.eliminar_curso, name='eliminar_curso'),
    path('admin_panel/cursos/asignar_profesores/<int:pk>/', views.asignar_profesores, name='asignar_profesores'),
    path('admin_panel/quejas/', views.ver_quejas, name='ver_quejas'),  # Página de visualización de quejas

    path('', lambda request: redirect('login')),  # Redirigir la ruta raíz al login
]
