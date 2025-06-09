from django.shortcuts import render, redirect, get_object_or_404
from dashboard.models import Project
from dashboard.forms import ProjectMessageForm
from dashboard.views import project_access_required
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages

@project_access_required
@require_http_methods(["GET", "POST"])
def project_chat(request, pk):
    project = get_object_or_404(Project, pk=pk)
    messages_qs = project.messages.select_related('sender').order_by('timestamp')
    message_form = ProjectMessageForm(request.POST or None)

    # Обработка очистки чата
    if request.method == 'POST':
        if 'clear_chat' in request.POST and request.user.role in ('ADMIN', 'DIRECTOR'):
            project.messages.all().delete()
            messages.success(request, "Чат успешно очищен.")
            return redirect('dashboard:project_chat', pk=pk)

    if request.method == 'POST' and ('send_message' in request.POST or 'attachment' in request.FILES):
        message_form = ProjectMessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            msg = message_form.save(commit=False)
            msg.project = project
            msg.sender = request.user
            msg.save()
            return redirect('dashboard:project_chat', pk=pk)


    return render(request, 'dashboard/projects/chat/project_chat.html', {
        'project': project,
        'messages': messages_qs,
        'message_form': message_form
    })
@login_required
def fetch_project_messages(request, pk):
    project = get_object_or_404(Project, pk=pk)
    messages = project.messages.select_related('sender').order_by('timestamp')
    data = []
    for msg in messages:
        data.append({
            'sender': msg.sender.get_full_name(),
            'is_user': msg.sender == request.user,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            'attachment_url': msg.attachment.url if msg.attachment else ''
        })
    return JsonResponse({'messages': data})