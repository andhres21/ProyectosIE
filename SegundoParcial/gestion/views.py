from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required  # Para proteger la vista del admin
from .models import Curso, Inventario, Bitacora, Usuario, AsignacionCurso
from .forms import CrearUsuarioForm, EditarUsuarioForm, CrearCursoForm, AsignarProfesoresForm
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import logout


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
    cursos = request.user.cursos.all()  # Obtener los cursos asignados al alumno
    return render(request, 'gestion/alumno_panel.html', {'cursos': cursos})  # Renderiza la plantilla correspondiente

@login_required
def instructor_panel(request):
    cursos = Curso.objects.filter(profesores=request.user)  # Filtrar cursos asignados al instructor
    inventario = Inventario.objects.filter(asignado_a=request.user)  # Obtener inventario asignado al instructor
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
    registros = Bitacora.objects.all().order_by('-fecha_hora')
    return render(request, 'gestion/ver_bitacora.html', {'registros': registros})

# Página para asignar inventario a los instructores
def asignar_inventario(request):
    return render(request, 'gestion/asignar_inventario.html')

# Página para visualizar quejas (temporalmente solo con texto)
def ver_quejas(request):
    return render(request, 'gestion/ver_quejas.html')

# Vista para la creación de usuarios
def admin_credenciales(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Determinar el rol del usuario basado en los campos booleanos
                if user.is_admin:
                    rol = "Administrador"
                elif user.is_instructor:
                    rol = "Instructor"
                elif user.is_alumno:
                    rol = "Alumno"
                else:
                    rol = "Sin rol"

                # Registrar la creación del usuario en la bitácora
                accion = f"Creación del usuario {user.username} con rol {rol}"
                registrar_accion(request.user, accion)

                return redirect('admin_credenciales')
            except Exception as e:
                form.add_error(None, f"Error al crear el usuario: {e}")
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
    if request.method == 'POST':
        # Manejar la creación de un curso
        if 'crear_curso' in request.POST:
            crear_curso_form = CrearCursoForm(request.POST)
            if crear_curso_form.is_valid():
                curso = crear_curso_form.save()
                registrar_accion(request.user, f"Se creó el curso {curso.nombre}")
                return redirect('asignar_cursos')
    else:
        crear_curso_form = CrearCursoForm()

    # Obtener los cursos y sus asignaciones
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
            secciones[asignacion.seccion] = asignacion.profesor.username if asignacion.profesor else 'Sin asignar'

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
    instructores = Usuario.objects.filter(is_instructor=True)  # Obtener solo los instructores
    
    if request.method == 'POST':
        # Procesar las asignaciones de secciones
        seccion_a_instructor_id = request.POST.get('seccion_a')
        seccion_b_instructor_id = request.POST.get('seccion_b')
        seccion_c_instructor_id = request.POST.get('seccion_c')

        # Asignar instructores a las secciones correspondientes (permitir sin asignar)
        if seccion_a_instructor_id:
            instructor_a = get_object_or_404(Usuario, pk=seccion_a_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='A', defaults={'profesor': instructor_a})
        else:
            # Si no se selecciona un instructor, la sección queda sin asignar
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='A', defaults={'profesor': None})

        if seccion_b_instructor_id:
            instructor_b = get_object_or_404(Usuario, pk=seccion_b_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='B', defaults={'profesor': instructor_b})
        else:
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='B', defaults={'profesor': None})

        if seccion_c_instructor_id:
            instructor_c = get_object_or_404(Usuario, pk=seccion_c_instructor_id)
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='C', defaults={'profesor': instructor_c})
        else:
            AsignacionCurso.objects.update_or_create(curso=curso, seccion='C', defaults={'profesor': None})

        return redirect('asignar_cursos')

    return render(request, 'gestion/asignar_profesores.html', {'curso': curso, 'instructores': instructores})


@login_required
@staff_member_required
def inventario_view(request):
    if request.method == 'POST':    
        # Crear un nuevo producto
        nombre = request.POST.get('nombre')
        cantidad = int(request.POST.get('cantidad_total'))
        Inventario.objects.create(nombre=nombre, cantidad_total=cantidad)
        return redirect('inventario')  # Redirige a la misma página

    inventario = Inventario.objects.all()
    return render(request, 'gestion/inventario.html', {'inventario': inventario})
