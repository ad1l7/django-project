import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from dashboard.models import PersonalTask

@login_required
def kanban_board(request):
    tasks = PersonalTask.objects.filter(user=request.user)
    return render(request, 'dashboard/dashboard.html', {'tasks': tasks})

@csrf_exempt
@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            PersonalTask.objects.create(user=request.user, title=title)
    return redirect('dashboard:home')

@csrf_exempt
@login_required
def update_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')
        task = get_object_or_404(PersonalTask, id=task_id, user=request.user)
        task.status = new_status
        task.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@require_POST
@login_required
def delete_personal_task(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        task = get_object_or_404(PersonalTask, id=task_id, user=request.user)
        task.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
