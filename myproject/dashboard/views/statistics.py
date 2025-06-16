from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from dashboard.models import Project, ProjectParticipant, Task
from users.models import User
from collections import defaultdict

@login_required
@user_passes_test(lambda u: u.role in ['ADMIN', 'DIRECTOR'])
def statistics(request, pk):
    project = get_object_or_404(Project, id=pk)

    # Утвержденные работники проекта
    approved_workers_qs = ProjectParticipant.objects.filter(
        project=project,
        status='approved',
        worker__role='WORKER'
    ).select_related('worker')

    # Все админы и директоры
    admins_directors_qs = User.objects.filter(role__in=['ADMIN', 'DIRECTOR'])

    # Собираем всех нужных пользователей в словарь {id: user}
    users = {p.worker.id: p.worker for p in approved_workers_qs}
    for user in admins_directors_qs:
        users[user.id] = user  # добавим или перезапишем

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

    stats.sort(key=lambda x: x['done'], reverse=True)

    return render(request, 'dashboard/projects/statistics/project_statistics.html', {
        'project': project,
        'statistics': stats
    })
