from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from dashboard.models import Project
from dashboard.views import project_access_required

@project_access_required
def project_overview(request, pk):
    project = get_object_or_404(Project, pk=pk)
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status='done').count()

    progress = 0
    if total_tasks > 0:
        progress = int((completed_tasks / total_tasks) * 100)

    return render(request, 'dashboard/project_overview.html', {
        'project': project,
        'progress': progress,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
    })
