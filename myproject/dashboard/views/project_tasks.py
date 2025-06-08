from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from dashboard.models import Project, Task
from dashboard.forms import TaskForm
from dashboard.views import project_access_required

@project_access_required
def project_tasks(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    form = TaskForm(request.POST or None, request.FILES or None)

    if request.user.role in (Project.DIRECTOR, Project.ADMIN):
        if request.method == 'POST' and form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            return redirect('dashboard:project_tasks', pk=pk)
    else:
        form = None

    return render(request, 'dashboard/project_tasks.html', {
        'project': project,
        'tasks': tasks,
        'form': form,
    })


@user_passes_test(lambda u: u.is_authenticated and u.role in ('DIRECTOR', 'ADMIN'), login_url='users:auth')
def create_task(request):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.project = Project.objects.first()  # либо выбрать из формы
            task.save()
            return redirect('dashboard:tasks_list')
    return render(request, 'dashboard/create_task.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.role in ('DIRECTOR', 'ADMIN'), login_url='users:auth')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача обновлена.')
            return redirect(f"{request.GET.get('next', '/dashboard/tasks/?project_id=' + str(task.project.id))}")
    else:
        form = TaskForm(instance=task)
    return render(request, 'dashboard/edit_task.html', {'form': form, 'task': task})


@user_passes_test(lambda u: u.is_authenticated and u.role in ('DIRECTOR', 'ADMIN'), login_url='users:auth')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.created_by != request.user:
        messages.error(request, 'Вы не можете удалить эту задачу.')
        return redirect('dashboard:tasks_list')
    task.delete()
    messages.success(request, 'Задача успешно удалена.')
    return redirect(request.META.get('HTTP_REFERER', '/dashboard/tasks/'))


@login_required
def tasks_list(request):
    project = None
    project_id = request.GET.get('project_id')

    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            project = None

    tasks = Task.objects.filter(project=project) if project else Task.objects.none()
    form = TaskForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid() and request.user.role in ('DIRECTOR', 'ADMIN'):
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        return redirect(f'{request.path}?project_id={project.id}')

    return render(request, 'dashboard/tasks_list.html', {
        'project': project,
        'tasks': tasks,
        'form': form,
    })
