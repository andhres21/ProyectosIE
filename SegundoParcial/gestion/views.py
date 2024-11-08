from django.contrib import messages  # Importa el sistema de mensajes de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required  # Para proteger la vista del admin
from .models import PagoCurso, Queja, Curso, Inventario, Bitacora, Usuario, AsignacionCurso, AsignacionInventario, Reporte, Retroalimentacion
from .forms import PagoCursoForm, QuejaForm, CrearUsuarioForm, EditarUsuarioForm, CrearCursoForm, AsignarInventarioForm, ReporteForm, RetroalimentacionForm
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import logout
from django.db.models import F, Sum
from django.http import HttpResponseForbidden
from django.urls import reverse

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            registrar_accion(user, "Inicio de sesión exitoso")
            # Redirigir según el rol
            if user.is_admin:
                return redirect('admin_panel')
            elif user.is_instructor:
                return redirect('instructor_panel')
            elif user.is_alumno:
                return redirect('alumno_panel')
        else:
            # Mostrar un error si el login falla
            return render(request, 'gestion/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'gestion/login.html')


@login_required
def alumno_panel(request):
    registrar_accion(request.user, "Accedió al portal estudiantil")
    cursos_asignados = request.user.cursos_asignados.all()  # Get courses the student is already assigned to
    return render(request, 'gestion/alumno_panel.html', {'cursos_asignados': cursos_asignados})  # Render assigned courses

@login_required
def instructor_panel(request):
    # Filtrar los cursos asignados al instructor
    registrar_accion(request.user, "Accedió al panel de instructor")
    cursos = Curso.objects.filter(instructor=request.user)  
    
    # Filtrar inventario asignado al instructor actual (request.user)
    inventario = Inventario.objects.filter(asignado_a=request.user)  
    
    return render(request, 'gestion/instructor_panel.html', {'cursos': cursos, 'inventario': inventario})


@login_required
@staff_member_required  # Solo accesible por personal con permisos de administrador
def admin_panel(request):
    return render(request, 'gestion/admin_panel.html')  # Renderiza la plantilla del administrador

Usuario = get_user_model()

def registrar_accion(usuario, accion):
    if isinstance(usuario, SimpleLazyObject):
        usuario = Usuario.objects.get(pk=usuario.pk)  # Asegúrate de usar Usuario personalizado
    bitacora = Bitacora(usuario=usuario, accion=accion, fecha_hora=timezone.now())
    bitacora.save()

# Página para visualizar la bitácora
def ver_bitacora(request):
    registrar_accion(request.user, "Accedió a la bitácora")
    registros = Bitacora.objects.all().order_by('-fecha_hora')
    return render(request, 'gestion/ver_bitacora.html', {'registros': registros})

@login_required
@staff_member_required
def borrar_historial(request):
    if request.method == 'POST':
        # Eliminar todos los registros de la bitácora
        Bitacora.objects.all().delete()
        registrar_accion(request.user, "Reinicio de la bitácora")
        # Registrar en la bitácora que se borró el historial
        registrar_accion(request.user, "Reinicio de la bitácora")
    
    return redirect('ver_bitacora')

# Vista para la creación de usuarios
def admin_credenciales(request):
    if request.method == 'POST':
        print(request.POST)
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                rol = "Sin rol"
                if user.is_admin:
                    rol = "Administrador"
                elif user.is_instructor:
                    rol = "Instructor"
                elif user.is_alumno:
                    rol = "Alumno"
                
                # Registrar en la bitácora
                accion = f"Creación del usuario {user.username} con rol {rol}"
                registrar_accion(request.user, accion)

                # Mensaje de éxito
                messages.success(request, f"Usuario '{user.username}' creado exitosamente con rol {rol}.")
                return redirect('admin_credenciales')
            except Exception as e:
                form.add_error(None, f"Error al crear el usuario: {e}")
                messages.error(request, "Ocurrió un error al intentar crear el usuario.")
        else:
            # Imprimir errores específicos del formulario en la consola
            print(form.errors)
            messages.error(request, "Error en el formulario. Revisa los datos ingresados.")
    else:
        form = CrearUsuarioForm()

    usuarios = Usuario.objects.all()
    return render(request, 'gestion/admin_credenciales.html', {'form': form, 'usuarios': usuarios})


# Vista para editar un usuario existente
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            antiguo_username = usuario.username  # Guardar el nombre anterior antes de cambiar
            user = form.save()
            # Registrar el cambio en la bitácora
            if antiguo_username != user.username:
                accion = f"El usuario {request.user.username} cambió el nombre de {antiguo_username} a {user.username}"
            else:
                accion = f"El usuario {request.user.username} editó los datos de {user.username}"

            registrar_accion(request.user, accion)
            return redirect('admin_credenciales')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'gestion/editar_usuario.html', {'form': form, 'usuario': usuario})

def logout_view(request):
    registrar_accion(request.user, "Cerró sesión")
    logout(request)
    return redirect('login')

@login_required
@staff_member_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        username = usuario.username  # Guardamos el nombre antes de eliminar
        usuario.delete()
        
        # Registrar en la bitácora
        accion = f'Se eliminó a {username}'
        registrar_accion(request.user, accion)  # El usuario actual realiza la acción de eliminar
        return redirect('admin_credenciales')
    
    return render(request, 'gestion/confirmar_eliminar.html', {'usuario': usuario})

@login_required
@staff_member_required
def asignar_cursos(request):
    # Verificamos si se ha enviado el formulario
    if request.method == 'POST':
        crear_curso_form = CrearCursoForm(request.POST)  # Instancia el formulario con los datos del POST
        if crear_curso_form.is_valid():
            curso = crear_curso_form.save()  # Guarda el nuevo curso
            registrar_accion(request.user, f"Se creó el curso {curso.nombre}")  # Registra la acción en la bitácora
            messages.success(request, "Curso creado exitosamente.")
            return redirect('asignar_cursos')  # Redirige para evitar reenviar el formulario en una recarga
        else:
            messages.error(request, "Error al crear el curso. Verifica los datos ingresados.")
    else:
        # Si no hay POST, inicializa un formulario vacío para la creación de curso
        crear_curso_form = CrearCursoForm()

    # Obtener los cursos existentes y las secciones asignadas
    cursos_con_secciones = []
    cursos = Curso.objects.all()
    for curso in cursos:
        asignaciones = AsignacionCurso.objects.filter(curso=curso)
        secciones = {
            'A': 'Sin asignar',
            'B': 'Sin asignar',
            'C': 'Sin asignar'
        }
        for asignacion in asignaciones:
            secciones[asignacion.seccion] = asignacion.instructor.username if asignacion.instructor else 'Sin asignar'

        cursos_con_secciones.append({
            'curso': curso,
            'seccion_a': secciones['A'],
            'seccion_b': secciones['B'],
            'seccion_c': secciones['C'],
        })

    context = {
        'crear_curso_form': crear_curso_form,
        'cursos_con_secciones': cursos_con_secciones,
    }
    return render(request, 'gestion/asignar_cursos.html', context)


# Vista para editar un curso existente
@login_required
@staff_member_required
def editar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    
    if request.method == 'POST':
        form = CrearCursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            registrar_accion(request.user, f"Se editó el curso {curso.nombre}")
            return redirect('asignar_cursos')  # Redirigir de nuevo a la lista de cursos
    else:
        form = CrearCursoForm(instance=curso)
    
    return render(request, 'gestion/editar_curso.html', {'form': form, 'curso': curso})

@login_required
@staff_member_required
def eliminar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        nombre_curso = curso.nombre  # Guardar el nombre del curso antes de eliminarlo
        
        # Limpiar la relación ManyToMany con los alumnos
        curso.alumnos.clear()  # Elimina todas las relaciones con los alumnos

        # Eliminar todas las asignaciones de ese curso
        AsignacionCurso.objects.filter(curso=curso).delete()

        curso.delete()

        # Registrar la eliminación del curso en la bitácora
        accion = f"Se eliminó el curso {nombre_curso}"
        registrar_accion(request.user, accion)

        return redirect('asignar_cursos')

    return render(request, 'gestion/confirmar_eliminar_curso.html', {'curso': curso})


@login_required
@staff_member_required
def asignar_profesores(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    instructores = Usuario.objects.filter(is_instructor=True)  # Make sure this retrieves only instructors

    if request.method == 'POST':
        # Process the POST data for section assignments
        seccion_a_instructor_id = request.POST.get('seccion_A')
        seccion_b_instructor_id = request.POST.get('seccion_B')
        seccion_c_instructor_id = request.POST.get('seccion_C')

        # Assign instructors to sections if provided, else leave unassigned
        if seccion_a_instructor_id:
            instructor_a = get_object_or_404(Usuario, pk=seccion_a_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='A', defaults={'instructor': instructor_a})
        else:
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='A', defaults={'instructor': None})

        if seccion_b_instructor_id:
            instructor_b = get_object_or_404(Usuario, pk=seccion_b_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='B', defaults={'instructor': instructor_b})
        else:
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='B', defaults={'instructor': None})

        if seccion_c_instructor_id:
            instructor_c = get_object_or_404(Usuario, pk=seccion_c_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='C', defaults={'instructor': instructor_c})
        else:
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='C', defaults={'instructor': None})

        return redirect('asignar_cursos')  # Redirect to courses overview after assignments

    return render(request, 'gestion/asignar_profesores.html', {'curso': curso, 'instructores': instructores})

@login_required
@staff_member_required
def inventario_view(request):
    if request.method == 'POST':    
        nombre = request.POST.get('nombre')
        cantidad = int(request.POST.get('cantidad_total'))

        # Verificar si el artículo ya existe
        inventario_existente = Inventario.objects.filter(nombre=nombre).first()
        if inventario_existente:
            # Si existe, sumar la cantidad
            inventario_existente.cantidad_total += cantidad
            inventario_existente.cantidad_disponible += cantidad
            inventario_existente.save()
            registrar_accion(request.user, f"Agregó {cantidad} unidades de {nombre} al inventario existente")
        else:
            # Si no existe, crear un nuevo registro
            Inventario.objects.create(nombre=nombre, cantidad_total=cantidad, cantidad_disponible=cantidad)
            registrar_accion(request.user, f"Creó {cantidad} unidades de {nombre} en el inventario")
        
        return redirect('inventario')  # Redirige a la misma página

    inventario = Inventario.objects.all()
    return render(request, 'gestion/inventario.html', {'inventario': inventario})


@login_required
@staff_member_required
def asignar_inventario(request):
    if request.method == 'POST':
        form = AsignarInventarioForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            inventario = asignacion.inventario
            
            # Validar que la cantidad solicitada no exceda la disponible
            if asignacion.cantidad_asignada > inventario.cantidad_disponible:
                form.add_error('cantidad_asignada', 'La cantidad asignada excede la cantidad disponible.')
            else:
                # Actualizar el inventario
                inventario.cantidad_prestada += asignacion.cantidad_asignada
                inventario.save()
                
                # Guardar la asignación
                asignacion.save()
                
                # Registrar en la bitácora
                registrar_accion(request.user, f"Asignó {asignacion.cantidad_asignada} unidades de {inventario.nombre} a {asignacion.usuario.username}")
                return redirect('inventario')
    else:
        form = AsignarInventarioForm()
    
    return render(request, 'gestion/asignar_inventario.html', {'form': form})


@login_required
@staff_member_required
def devolver_inventario(request):
    # Obtener todas las asignaciones
    asignaciones = AsignacionInventario.objects.all()

    # Procesar las devoluciones
    if request.method == 'POST':
        asignacion_id = request.POST.get('asignacion_id')
        cantidad_devolver = int(request.POST.get('cantidad_devolver'))

        # Si la cantidad a devolver es 0, no hacer nada y redirigir
        if cantidad_devolver == 0:
            return redirect('devolver_inventario')

        # Obtener la asignación específica
        asignacion = AsignacionInventario.objects.get(id=asignacion_id)

        # Verificar que no se devuelvan más productos de los asignados
        if cantidad_devolver <= asignacion.cantidad_asignada:
            # Actualizar el inventario y la asignación
            asignacion.inventario.cantidad_disponible += cantidad_devolver
            asignacion.inventario.cantidad_prestada -= cantidad_devolver
            asignacion.inventario.save()

            asignacion.cantidad_asignada -= cantidad_devolver
            asignacion.save()

            # Registrar en la bitácora
            registrar_accion(request.user, f"{asignacion.usuario.username} devolvió {cantidad_devolver} unidades de {asignacion.inventario.nombre} al inventario")

            # Si la cantidad asignada llega a 0, eliminar la asignación
            if asignacion.cantidad_asignada == 0:
                asignacion.delete()

        return redirect('devolver_inventario')  # Redirigir para actualizar la lista

    # Filtrar solo las asignaciones con cantidad asignada mayor a 0
    asignaciones = AsignacionInventario.objects.filter(cantidad_asignada__gt=0)

    return render(request, 'gestion/devolver_inventario.html', {'asignaciones': asignaciones})

@login_required
@staff_member_required
def eliminar_inventario(request, pk):
    # Obtener el producto del inventario
    inventario = get_object_or_404(Inventario, pk=pk)
    
    # Eliminar todas las asignaciones relacionadas con este producto
    AsignacionInventario.objects.filter(inventario=inventario).delete()

    # Registrar en la bitácora antes de eliminar el producto
    registrar_accion(request.user, f"Eliminó el artículo {inventario.nombre} del inventario y sus asignaciones")

    # Eliminar el producto del inventario
    inventario.delete()

    # Redirigir de vuelta a la página de inventario
    return redirect('inventario')

@login_required
def asignar_curso_alumno(request, curso_id):
    curso_asignado = get_object_or_404(AsignacionCurso, id=curso_id)

    # Verifica si el curso tiene cupos disponibles y si ya se ha pagado
    pago_existente = PagoCurso.objects.filter(alumno=request.user, curso=curso_asignado.curso).exists()
    
    if curso_asignado.cupo_disponible() > 0 and not pago_existente:
        # Registrar el pago
        PagoCurso.objects.create(
            alumno=request.user,
            curso=curso_asignado.curso,
            monto_pagado=curso_asignado.curso.costo
        )
        
        # Asigna al alumno al curso
        curso_asignado.asignar_alumno(request.user)
        registrar_accion(request.user, f"Pagó y se inscribió al curso {curso_asignado.curso.nombre} por ${curso_asignado.curso.costo}")
        return redirect('asignar_cursos_alumno')
    else:
        return render(request, 'gestion/asignar_cursos_alumno.html', {'error': 'No hay cupos disponibles o ya has pagado este curso.'})
    
@login_required
def desasignar_curso_alumno(request, curso_id):
    curso_asignado = get_object_or_404(AsignacionCurso, id=curso_id)

    # Desasigna el alumno
    if curso_asignado.desasignar_alumno(request.user):
        registrar_accion(request.user, f"Se desasignó del curso {curso_asignado.curso.nombre}")
        return redirect('asignar_cursos_alumno')

    return render(request, 'gestion/asignar_cursos_alumno.html', {'error': 'No estás asignado a este curso'})

@login_required
@login_required
def asignar_cursos_alumno(request):
    # Filtrar cursos disponibles que tienen cupo, excluyendo aquellos sin instructor y en los que el alumno ya esté asignado o pagado
    cursos_disponibles = AsignacionCurso.objects.filter(
        cupo_ocupado__lt=F('cupo_maximo'),
        instructor__isnull=False  # Excluir cursos sin instructor
    ).exclude(alumnos=request.user)

    # Agregar un campo booleano para cada curso indicando si el alumno ya ha pagado
    cursos_disponibles_info = []
    for curso_asignacion in cursos_disponibles:
        pago_realizado = PagoCurso.objects.filter(alumno=request.user, curso=curso_asignacion.curso).exists()
        # Solo añadir a cursos_disponibles_info si no se ha pagado el curso
        if not pago_realizado:
            cursos_disponibles_info.append({
                'curso': curso_asignacion,
                'pago_realizado': pago_realizado
            })

    # Mostrar los cursos en los que el alumno ya está asignado
    cursos_asignados = AsignacionCurso.objects.filter(alumnos=request.user)

    context = {
        'cursos_disponibles_info': cursos_disponibles_info,
        'cursos_asignados': cursos_asignados
    }
    
    return render(request, 'gestion/asignar_cursos_alumno.html', context)

    
@login_required
def atencion_cliente(request):
    if request.method == 'POST':
        form = QuejaForm(request.POST)
        if form.is_valid():
            queja = form.save(commit=False)
            queja.alumno = request.user
            queja.save()
            registrar_accion(request.user, "Ingresó una queja")
            return redirect('atencion_cliente')
    else:
        form = QuejaForm()

    # Obtener todas las quejas del alumno actual
    quejas = Queja.objects.filter(alumno=request.user).order_by('-fecha')
    
    # Obtener todas las retroalimentaciones del alumno actual
    retroalimentaciones = Retroalimentacion.objects.filter(alumno=request.user).order_by('-fecha_envio')

    return render(request, 'gestion/atencion_cliente.html', {
        'form': form, 
        'quejas': quejas, 
        'retroalimentaciones': retroalimentaciones  # Añadimos las retroalimentaciones al contexto
    })

@login_required
@staff_member_required
def ver_quejas(request):
    registrar_accion(request.user, "Accedió a la vista de quejas y reportes")
    # Obtener todas las quejas de los alumnos
    quejas = Queja.objects.all().order_by('-fecha')

    # Obtener todos los reportes de los instructores
    reportes = Reporte.objects.all().order_by('-fecha')

    return render(request, 'gestion/ver_quejas.html', {'quejas': quejas, 'reportes': reportes})



@login_required
def ver_alumnos_asignados(request):
    # Verificar si el usuario es un instructor
    if not request.user.is_instructor:
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
    registrar_accion(request.user, "Accedió a la lista de alumnos asignados")
    cursos = AsignacionCurso.objects.filter(instructor=request.user)
    return render(request, 'gestion/ver_alumnos_asignados.html', {'cursos': cursos})

@login_required
def administrar_inscripciones(request):
    # Verificar si el usuario es un instructor
    if not request.user.is_instructor:
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
    registrar_accion(request.user, "Accedió a la administración de inscripciones")
    cursos = AsignacionCurso.objects.filter(instructor=request.user)
    return render(request, 'gestion/administrar_inscripciones.html', {'cursos': cursos})

@login_required
def desasignar_alumno(request, curso_id, alumno_id):
    # Verificar si el usuario es un instructor
    if not request.user.is_instructor:
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
    
    curso = get_object_or_404(AsignacionCurso, id=curso_id)
    alumno = get_object_or_404(Usuario, id=alumno_id)
    curso.desasignar_alumno(alumno)
    registrar_accion(request.user, f"Desasignó al alumno {alumno.username} del curso {curso.curso.nombre}")
    return redirect('administrar_inscripciones')

@login_required
def administrar_inventario(request):
    # Obtener solo el inventario asignado al instructor actual
    inventario_asignado = AsignacionInventario.objects.filter(usuario=request.user)
    
    return render(request, 'gestion/administrar_inventario.html', {'inventario': inventario_asignado})


@login_required
def enviar_reporte(request):
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.instructor = request.user  # Asignar el usuario actual al campo instructor
            reporte.save()
            registrar_accion(request.user, "Envió un reporte")
            # Redirigir con un parámetro `?success=true` para indicar éxito
            return redirect(f"{reverse('enviar_reporte')}?success=true")
    else:
        form = ReporteForm()

    # Verificar el parámetro `success` en la URL
    success = request.GET.get('success') == 'true'
    return render(request, 'gestion/enviar_reporte.html', {
        'form': form,
        'success': success
    })

@login_required
def enviar_retroalimentacion(request):
    if request.method == 'POST':
        form = RetroalimentacionForm(request.POST, instructor=request.user)
        if form.is_valid():
            retroalimentacion = form.save(commit=False)
            retroalimentacion.instructor = request.user  # Asigna el instructor actual
            retroalimentacion.save()
            # Redirigir con un parámetro `?success=true` para indicar éxito
            return redirect(f"{reverse('enviar_retroalimentacion')}?success=true")
    else:
        form = RetroalimentacionForm(instructor=request.user)  # <- Instructor como argumento
    
    # Verificar el parámetro `success` en la URL
    success = request.GET.get('success') == 'true'
    return render(request, 'gestion/enviar_retroalimentacion.html', {
        'form': form,
        'success': success
    })

@login_required
def ver_pagos(request):
    pagos = PagoCurso.objects.filter(alumno=request.user).order_by('-fecha_pago')
    return render(request, 'gestion/ver_pagos.html', {'pagos': pagos})

@login_required
@staff_member_required
def ver_contabilidad(request):
    ingresos_totales = PagoCurso.objects.aggregate(total=Sum('monto_pagado'))['total'] or 0
    pagos = PagoCurso.objects.select_related('alumno', 'curso').all().order_by('-fecha_pago')
    return render(request, 'gestion/ver_contabilidad.html', {'pagos': pagos, 'ingresos_totales': ingresos_totales})
    
@login_required
def pago_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar si el usuario ya ha pagado el curso
    pago_existente = PagoCurso.objects.filter(alumno=request.user, curso=curso).exists()
    if pago_existente:
        messages.info(request, "Ya has pagado este curso.")
        return redirect('asignar_cursos_alumno')

    if request.method == 'POST':
        form = PagoCursoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.alumno = request.user
            pago.curso = curso
            pago.monto_pagado = curso.costo
            pago.save()

            # Asignar automáticamente al alumno al curso después del pago
            curso.alumnos.add(request.user)
            curso.save()

            messages.success(request, f"Pago realizado con éxito y te has inscrito en el curso {curso.nombre}.")
            return redirect('asignar_cursos_alumno')
    else:
        form = PagoCursoForm(initial={'curso': curso, 'monto_pagado': curso.costo})

    return render(request, 'gestion/pago_curso.html', {'form': form, 'curso': curso})

