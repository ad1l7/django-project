from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from functools import wraps
from users.models import User
from users.forms import AdminRegisterForm, WorkerRegisterForm
from .models import Project, ProjectParticipant, ProjectMessage, Task
from .forms import ProjectForm, ProjectMessageForm, TaskForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.forms import ProfileForm


import logging
def is_director(user):
    return user.is_authenticated and user.role == User.DIRECTOR

def is_director_or_admin(user):
    return user.is_authenticated and user.role in (User.DIRECTOR, User.ADMIN)

@login_required(login_url='users:auth')
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('users:auth')

@login_required
def profile_view(request):
    return render(request, 'dashboard/profile.html', {
        'user': request.user
    })

@user_passes_test(is_director, login_url='users:auth')
def admins_view(request):
    admins = User.objects.filter(role=User.ADMIN)
    form = AdminRegisterForm()

    if request.method == 'POST':
        if 'create_admin' in request.POST:
            form = AdminRegisterForm(request.POST)
            if form.is_valid():
                admin = form.save(commit=False)
                admin.role = User.ADMIN
                admin.save()
                return redirect('dashboard:admins')
        elif 'delete_admin' in request.POST:
            admin_id = request.POST.get('admin_id')
            admin = get_object_or_404(User, id=admin_id, role=User.ADMIN)
            admin.delete()
            return redirect('dashboard:admins')

    return render(request, 'dashboard/admins.html', {'admins': admins, 'form': form})

@user_passes_test(is_director_or_admin, login_url='users:auth')
def workers_view(request):
    workers = User.objects.filter(role=User.WORKER)
    form = WorkerRegisterForm()

    if request.method == 'POST':
        if 'create_worker' in request.POST:
            form = WorkerRegisterForm(request.POST)
            if form.is_valid():
                worker = form.save(commit=False)
                worker.role = User.WORKER
                worker.save()
                return redirect('dashboard:workers')
        elif 'delete_worker' in request.POST:
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(User, id=worker_id, role=User.WORKER)
            worker.delete()
            return redirect('dashboard:workers')

    return render(request, 'dashboard/workers.html', {'workers': workers, 'form': form})

@user_passes_test(lambda u: u.is_authenticated, login_url='users:auth')
def projects_view(request):
    projects = Project.objects.all()
    form = None

    if request.user.role in (User.DIRECTOR, User.ADMIN):
        form = ProjectForm()
        if request.method == 'POST':
            if 'create_project' in request.POST:
                form = ProjectForm(request.POST, request.FILES)
                if form.is_valid():
                    project = form.save(commit=False)
                    project.created_by = request.user
                    project.save()
                    return redirect('dashboard:projects')
            elif 'edit_project' in request.POST:
                project_id = request.POST.get('project_id')
                project = get_object_or_404(Project, id=project_id)
                form = ProjectForm(request.POST, request.FILES, instance=project)
                if form.is_valid():
                    form.save()
                    return redirect('dashboard:projects')
            elif 'delete_project' in request.POST:
                project_id = request.POST.get('project_id')
                project = get_object_or_404(Project, id=project_id)
                project.delete()
                return redirect('dashboard:projects')

    return render(request, 'dashboard/projects.html', {'projects': projects, 'form': form})

from django.views.decorators.csrf import csrf_exempt

def project_access_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        if request.user.role in (User.DIRECTOR, User.ADMIN):
            return view_func(request, pk, *args, **kwargs)
        elif request.user.role == User.WORKER:
            participant = ProjectParticipant.objects.filter(project=project, worker=request.user).first()
            if participant and participant.status == 'approved':
                return view_func(request, pk, *args, **kwargs)
            else:
                return redirect('dashboard:project_access_denied_custom', pk=pk)
        return redirect('users:auth')
    return _wrapped_view

@login_required
def project_access_denied_custom(request, pk):
    project = get_object_or_404(Project, pk=pk)
    participant = ProjectParticipant.objects.filter(project=project, worker=request.user).first()

    if participant:
        if participant.status == 'rejected':
            message = "Ваша заявка была отклонена."
        else:
            message = "Ваша заявка рассматривается."
        show_apply = False
    else:
        message = "Вы не состоите в проекте. Хотите подать заявку?"
        show_apply = True

    if request.method == 'POST' and show_apply:
        ProjectParticipant.objects.create(project=project, worker=request.user, status='applied')
        return redirect('dashboard:project_access_denied_custom', pk=pk)

    return render(request, 'dashboard/project_access_denied.html', {
        'project': project,
        'message': message,
        'show_apply': show_apply,
    })

@project_access_required
def project_overview(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'dashboard/project_overview.html', {'project': project})

@project_access_required
def project_chat(request, pk):
    project = get_object_or_404(Project, pk=pk)
    messages = project.messages.select_related('sender').order_by('timestamp')
    message_form = ProjectMessageForm(request.POST or None)
    if request.method == 'POST' and message_form.is_valid():
        msg = message_form.save(commit=False)
        msg.project = project
        msg.sender = request.user
        msg.save()
        return redirect('dashboard:project_chat', pk=pk)
    return render(request, 'dashboard/project_chat.html', {'project': project, 'messages': messages, 'message_form': message_form})

@project_access_required
def project_participants(request, pk):
    project = get_object_or_404(Project, pk=pk)
    participants = project.participants.select_related('worker')
    workers = User.objects.filter(role=User.WORKER)

    if request.method == 'POST':
        if 'invite_worker' in request.POST:
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(User, id=worker_id, role=User.WORKER)
            ProjectParticipant.objects.get_or_create(project=project, worker=worker, defaults={'status': 'invited'})
            return redirect('dashboard:project_participants', pk=pk)

        elif 'approve_participant' in request.POST:
            participant_id = request.POST.get('participant_id')
            participant = get_object_or_404(ProjectParticipant, id=participant_id, project=project)
            participant.status = 'approved'
            participant.save()
            return redirect('dashboard:project_participants', pk=pk)

        elif 'reject_participant' in request.POST:
            participant_id = request.POST.get('participant_id')
            participant = get_object_or_404(ProjectParticipant, id=participant_id, project=project)
            participant.status = 'rejected'
            participant.save()
            return redirect('dashboard:project_participants', pk=pk)

    return render(request, 'dashboard/project_participants.html', {'project': project, 'participants': participants, 'workers': workers})

@project_access_required
def project_tasks(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    form = TaskForm(request.POST or None, request.FILES or None)

    if request.user.role in (User.DIRECTOR, User.ADMIN):
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

@user_passes_test(is_director_or_admin, login_url='users:auth')
def create_task(request):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.project = Project.objects.first()  # или выбор через форму позже
            task.save()
            return redirect('dashboard:tasks_list')
    return render(request, 'dashboard/create_task.html', {'form': form})

@user_passes_test(is_director_or_admin, login_url='users:auth')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.created_by != request.user:
        messages.error(request, 'Вы не можете удалить эту задачу.')
        return redirect('dashboard:tasks_list')
    task.delete()
    messages.success(request, 'Задача успешно удалена.')
    return redirect(f"{request.META.get('HTTP_REFERER', '/dashboard/tasks/')}")

@user_passes_test(is_director_or_admin, login_url='users:auth')
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


@project_access_required
def rejected_participants(request, pk):
    project = get_object_or_404(Project, pk=pk)
    rejected = ProjectParticipant.objects.filter(project=project, status='rejected').select_related('worker')

    if request.method == 'POST' and 'reinvite_participant' in request.POST:
        participant_id = request.POST.get('participant_id')
        participant = get_object_or_404(ProjectParticipant, id=participant_id, project=project)
        participant.status = 'invited'
        participant.save()
        messages.success(request, f"{participant.worker.get_full_name()} повторно приглашен.")
        return redirect('dashboard:rejected_participants', pk=pk)

    return render(request, 'dashboard/rejected_participants.html', {
        'project': project,
        'rejected_participants': rejected,
    })
from django.views.decorators.http import require_POST

@require_POST
@login_required
def take_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.status == 'free':
        task.status = 'in_progress'
        task.assigned_to = request.user
        task.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@project_access_required
def my_tasks_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(assigned_to=request.user, project=project)

    return render(request, 'dashboard/my_tasks.html', {
        'project': project,
        'tasks': tasks,
    })
@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'dashboard/my_tasks.html', {'tasks': tasks})

@require_POST
@login_required
def drop_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
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
def submitted_tasks_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    tasks = Task.objects.filter(status='submitted', project=project).select_related('assigned_to')

    return render(request, 'dashboard/submitted_tasks.html', {
        'tasks': tasks,
        'project': project,
    })

@login_required
def approve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.role not in ['ADMIN', 'DIRECTOR']:
        return HttpResponseForbidden("Нет доступа")

    if request.method == 'POST':
        task.status = 'done'
        task.save()
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
def completed_tasks_view(request, pk):
    if request.user.role not in ['ADMIN', 'DIRECTOR']:
        return HttpResponseForbidden("Нет доступа")

    project = get_object_or_404(Project, pk=pk)

    tasks = Task.objects.filter(status='done', project=project).select_related('assigned_to')

    return render(request, 'dashboard/completed_tasks.html', {
        'tasks': tasks,
        'project': project,
    })
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard:profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'dashboard/profile.html', {
        'user': user,
        'form': form
    })