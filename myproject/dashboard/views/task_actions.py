from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from dashboard.models import Task, Project
from dashboard.views import project_access_required

@require_POST
@login_required
def take_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # ✅ Учитываем только активные задачи (НЕ считаем done и free)
    active_tasks_count = Task.objects.filter(
        assigned_to=request.user,
        status__in=['in_progress', 'submitted']  # 🔥 'done' больше не учитывается!
    ).count()

    if active_tasks_count > 3:
        messages.error(request, 'Вы не можете взять больше 3 задач одновременно. Завершите текущие задачи.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if task.status == 'free':
        task.status = 'in_progress'
        task.assigned_to = request.user
        task.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
@login_required
def drop_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.canceled_by = request.user  # 💡 сохраняем, кто отменил задачу
    task.assigned_to = None
    task.status = 'free'
    task.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    comment = request.POST.get('comment')
    file = request.FILES.get('file')

    if file or comment:
        task.status = 'submitted'
        task.submitted_comment = comment
        if file:
            task.submitted_file = file
        task.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def approve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.role not in ['ADMIN', 'DIRECTOR']:
        return HttpResponseForbidden("Нет доступа")

    if request.method == 'POST':
        task.status = 'done'
        task.save()

        if task.assigned_to:
            task.assigned_to.total_reward += task.reward
            task.assigned_to.save()

    return redirect('dashboard:submitted_tasks', pk=task.project.id)

@login_required
def reject_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.role not in ['ADMIN', 'DIRECTOR']:
        return HttpResponseForbidden("Нет доступа")

    if request.method == 'POST':
        task.status = 'in_progress'
        task.submitted_comment = request.POST.get('comment', '')
        if request.FILES.get('file'):
            task.submitted_file = request.FILES['file']
        task.save()

    return redirect('dashboard:submitted_tasks', pk=task.project.id)

@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'dashboard/my_tasks/my_tasks.html', {'tasks': tasks})

@project_access_required
@login_required
def my_tasks_view(request, pk):
    project = get_object_or_404(Project, id=pk)
    tasks = Task.objects.filter(project=project, assigned_to=request.user)

    taken_tasks = tasks.exclude(status='free')
    total_taken = taken_tasks.count()
    done_count = taken_tasks.filter(status='done').count()
    progress = int((done_count / total_taken) * 100) if total_taken > 0 else 0

    return render(request, 'dashboard/my_tasks/my_tasks.html', {
        'project': project,
        'tasks': tasks,
        'progress': progress,
        'done_count': done_count,
        'total_taken': total_taken,
    })

@login_required
def submitted_tasks_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(status='submitted', project=project).select_related('assigned_to')

    return render(request, 'dashboard/projects/tasks/submitted_tasks.html', {
        'tasks': tasks,
        'project': project,
    })

@login_required
def completed_tasks_view(request, pk):
    if request.user.role not in ['ADMIN', 'DIRECTOR']:
        return HttpResponseForbidden("Нет доступа")

    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(status='done', project=project).select_related('assigned_to')

    return render(request, 'dashboard/projects/tasks/completed_tasks.html', {
        'tasks': tasks,
        'project': project,
    })
