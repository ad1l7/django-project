from django.shortcuts import render, redirect, get_object_or_404
from dashboard.models import Project
from dashboard.models import ProjectMessage
from dashboard.forms import ProjectMessageForm
from dashboard.views import project_access_required

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

    return render(request, 'dashboard/projects/chat/project_chat.html', {
        'project': project,
        'messages': messages,
        'message_form': message_form
    })
