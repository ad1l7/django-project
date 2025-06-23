from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from dashboard.models import Project, ProjectParticipant, Task
from users.models import User
import json

@login_required
@user_passes_test(lambda u: u.role in ['ADMIN', 'DIRECTOR'])
def statistics(request, pk):
    project = get_object_or_404(Project, id=pk)

    # Таблица статистики
    approved_workers_qs = ProjectParticipant.objects.filter(
        project=project,
        status='approved',
        worker__role='WORKER'
    ).select_related('worker')

    admins_directors_qs = User.objects.filter(role__in=['ADMIN', 'DIRECTOR'])

    users = {p.worker.id: p.worker for p in approved_workers_qs}
    for user in admins_directors_qs:
        users[user.id] = user

    stats = []
    for user in users.values():
        tasks = Task.objects.filter(project=project, assigned_to=user)

        stats.append({
            "name": user.get_full_name() or user.username,
            "role": {
                'WORKER': '👷 Работник',
                'ADMIN': '🧑‍💼 Админ',
                'DIRECTOR': '👨‍💼 Директор'
            }.get(user.role, '—'),
            "done": tasks.filter(status='done').count(),
            "canceled": Task.objects.filter(project=project, canceled_by=user).count(),
            "reward": sum(tasks.filter(status='done').values_list('reward', flat=True)),
            "total": tasks.exclude(status='free').count(),
        })

    # Дедлайны задач для календаря
    tasks = Task.objects.filter(project=project)
    calendar_events = []
    for task in tasks:
        if task.deadline and task.assigned_to:
            color = (
                "#28a745" if task.status == "done" else
                "#ffc107" if task.status == "in_progress" else
                "#0d6efd" if task.status == "submitted" else
                "#adb5bd"
            )
            calendar_events.append({
                "title": f"{task.title} - {task.assigned_to.get_full_name()}",
                "start": task.deadline.strftime('%Y-%m-%d'),
                "color": color
            })
    return render(request, 'dashboard/projects/statistics/project_statistics.html', {
        'project': project,
        'statistics': stats,
        'calendar_events': json.dumps(calendar_events, ensure_ascii=False)
    })
