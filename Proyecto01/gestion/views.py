from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .forms import ProfesorCreationForm
from .forms import CursoForm
from .models import Curso, Usuario
from django.shortcuts import get_object_or_404, redirect

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Iniciar sesión automáticamente después del registro
            return redirect('home')  # Redirigir a una página principal después del registro
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


def home(request):
    return HttpResponse("Bienvenido a la página principal")

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')  # Redirigir a la página de Administrador
    elif user.role == 'profesor':
        return redirect('profesor_dashboard')  # Redirigir a la página de Catedrático
    elif user.role == 'estudiante':
        return redirect('estudiante_dashboard')  # Redirigir a la página de Estudiante
    else:
        return redirect('home')  # Redirigir a la página de inicio si no tiene un rol
    
# Vista para Administrador
@login_required
def admin_dashboard(request):
    return HttpResponse("Bienvenido Administrador")

# Vista para Catedrático
@login_required
def profesor_dashboard(request):
    return HttpResponse("Bienvenido Catedrático")

# Vista para Estudiante
@login_required
def estudiante_dashboard(request):
    return HttpResponse("Bienvenido Estudiante")

# Verifica si el usuario es administrador
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def agregar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_cursos')
    else:
        form = CursoForm()
    return render(request, 'gestion/agregar_curso.html', {'form': form})

@user_passes_test(is_admin)
def agregar_profesor(request):
    if request.method == 'POST':
        form = ProfesorCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_profesores')
    else:
        form = ProfesorCreationForm()
    return render(request, 'gestion/agregar_profesor.html', {'form': form})

@user_passes_test(is_admin)
def lista_profesores(request):
    profesores = Usuario.objects.filter(role='profesor')
    return render(request, 'gestion/lista_profesores.html', {'profesores': profesores})


# Vista para listar los cursos
def lista_cursos(request):
    cursos = Curso.objects.all()  # Obtiene todos los cursos
    return render(request, 'gestion/lista_cursos.html', {'cursos': cursos})  # Renderiza la plantilla con los cursos

@login_required
def lista_cursos_estudiante(request):
    cursos = Curso.objects.all()
    return render(request, 'gestion/lista_cursos_estudiante.html', {'cursos': cursos})

@login_required
def asignarse_curso(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    if curso.cupo > 0:
        curso.estudiantes.add(request.user)
        curso.cupo -= 1
        curso.save()
        return redirect('lista_cursos_estudiante')
    else:
        return HttpResponse("No hay cupos disponibles")

@login_required
def inscribirse_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    usuario = request.user
    if usuario.role == 'estudiante':
        curso.estudiantes.add(usuario)
        return redirect('lista_cursos_estudiante')  # Redirige de nuevo a la lista de cursos
    else:
        return redirect('home')  # O redirige a otra vista si no es un estudiante

@login_required
def profesor_cursos(request):
    usuario = request.user
    if usuario.role == 'profesor':  # Asegurarse de que el usuario sea un profesor
        cursos = Curso.objects.filter(catedratico=usuario)  # Filtrar los cursos del profesor
        return render(request, 'gestion/profesor_cursos.html', {'cursos': cursos})
    else:
        return redirect('home')  # Si no es profesor, redirigir a otra vista
    
@login_required
def profesor_estudiantes(request, curso_id):
    usuario = request.user
    curso = get_object_or_404(Curso, id=curso_id, catedratico=usuario)  # Asegurarse de que el profesor imparte el curso
    estudiantes = curso.estudiantes.all()  # Obtener los estudiantes inscritos
    return render(request, 'gestion/profesor_estudiantes.html', {'curso': curso, 'estudiantes': estudiantes})

from .models import Nota
from django.shortcuts import get_object_or_404

@login_required
def profesor_asignar_nota(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id, catedratico=request.user)  # Verifica que el profesor imparte el curso
    estudiante = get_object_or_404(Usuario, id=estudiante_id, role='estudiante')  # Verifica que el usuario es un estudiante
    nota, created = Nota.objects.get_or_create(curso=curso, estudiante=estudiante)  # Obtener o crear una nota

    if request.method == 'POST':
        nota_valor = request.POST.get('nota')
        if nota_valor:  # Asegurarse de que el valor de la nota no sea nulo
            nota.nota = float(nota_valor)
            nota.save()
            return redirect('profesor_estudiantes', curso_id=curso.id)  # Redirige de nuevo a la lista de estudiantes
        else:
            # Si no se proporciona una nota, muestra un mensaje de error
            return render(request, 'gestion/profesor_asignar_nota.html', {'curso': curso, 'estudiante': estudiante, 'nota': nota, 'error': 'Debes proporcionar una nota válida.'})

    return render(request, 'gestion/profesor_asignar_nota.html', {'curso': curso, 'estudiante': estudiante, 'nota': nota})