from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User
from dashboard.models import Project, ProjectParticipant
from dashboard.forms import ProjectForm
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import threading
import time

@user_passes_test(lambda u: u.is_authenticated, login_url='users:auth')
def projects_view(request):
    projects = Project.objects.all()
    if request.GET.get('full') == 'true':
        messages.error(request, 'Лимит участников в этом проекте уже достигнут.')
    # 🔒 Только активные проекты для WORKER
    if request.user.role == User.WORKER:
        projects = projects.filter(is_closed=False)

    for project in projects:
        project.joined_workers = ProjectParticipant.objects.filter(project=project, status='approved').count()
        total = project.tasks.count()
        done = project.tasks.filter(status='done').count()
        project.total_tasks = total
        project.done_tasks = done
        project.progress = int((done / total) * 100) if total > 0 else 0

    if request.user.role in (User.DIRECTOR, User.ADMIN):
        form = ProjectForm()
        edit_forms = {p.id: ProjectForm(instance=p) for p in projects}

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

        return render(request, 'dashboard/projects/projects.html', {
            'projects': projects,
            'form': form,
            'edit_forms': edit_forms
        })
    
    # 🟡 Для WORKER — просто отображаем список проектов без форм
    return render(request, 'dashboard/projects/projects.html', {
        'projects': projects,
        'form': None,
        'edit_forms': {}
    })

def project_access_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        if request.user.role in (User.DIRECTOR, User.ADMIN):
            return view_func(request, pk, *args, **kwargs)
        elif request.user.role == User.WORKER:
            approved_count = ProjectParticipant.objects.filter(project=project, status='approved').count()

            if approved_count >= project.required_workers:
                return redirect(f'{reverse("dashboard:projects")}?full=true')


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
        current_count = ProjectParticipant.objects.filter(project=project, status='approved').count()
        if current_count >= project.required_workers:
            messages.error(request, 'Лимит участников проекта уже достигнут.')
            return redirect('dashboard:project_access_denied_custom', pk=pk)
        ProjectParticipant.objects.create(project=project, worker=request.user, status='applied')
        return redirect('dashboard:project_access_denied_custom', pk=pk)


    return render(request, 'dashboard/projects/access/project_access_denied.html', {
        'project': project,
        'message': message,
        'show_apply': show_apply,
    })

@login_required
@user_passes_test(lambda u: u.role in ('DIRECTOR', 'ADMIN'))
def close_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Установим "флаг закрытия"
    project.is_closed = True
    project.save()

    # Запускаем таймер в отдельном потоке
    def delayed_close():
        time.sleep(15)
        # Удалим всех работников-участников
        ProjectParticipant.objects.filter(project=project, worker__role='WORKER').delete()

    threading.Thread(target=delayed_close).start()

    messages.info(request, 'Проект будет завершен через 15 секунд. Вы можете отменить это действие.')
    return redirect('dashboard:project_overview', pk=pk)
