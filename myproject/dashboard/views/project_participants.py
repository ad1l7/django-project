from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.views import project_access_required
from users.models import User
from dashboard.models import Project, ProjectParticipant
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

@project_access_required
def project_participants(request, pk):
    project = get_object_or_404(Project, pk=pk)
    participants = project.participants.select_related('worker').exclude(status='rejected')

    # 👇 Исключаем всех участников проекта (в любом статусе) из выпадающего списка
    existing_worker_ids = project.participants.values_list('worker_id', flat=True)
    workers = User.objects.filter(role=User.WORKER).exclude(id__in=existing_worker_ids)

    if request.method == 'POST':
        if 'invite_worker' in request.POST:
            worker_id = request.POST.get('worker_id')
            if not worker_id:
                messages.error(request, "Пожалуйста, выберите сотрудника для приглашения.")
                return redirect('dashboard:project_participants', pk=pk)

            worker = get_object_or_404(User, id=worker_id, role=User.WORKER)

            participant, created = ProjectParticipant.objects.get_or_create(
                project=project,
                worker=worker,
                defaults={'status': 'approved', 'is_invited': True}
            )

            if not created:
                participant.status = 'approved'
                participant.is_invited = True
                participant.save()
                messages.warning(request, f"{worker.get_full_name()} уже был добавлен, статус обновлён.")
            else:
                messages.success(request, f"{worker.get_full_name()} успешно приглашён и утверждён.")

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

    return render(request, 'dashboard/projects/participants/project_participants.html', {
        'project': project,
        'participants': participants,
        'workers': workers
    })




@project_access_required
def rejected_participants(request, pk):
    project = get_object_or_404(Project, pk=pk)

    rejected = ProjectParticipant.objects.filter(
        project=project,
        status='rejected'
    ).select_related('worker')

    if request.method == 'POST':
        if 'approve_rejected' in request.POST:
            participant_id = request.POST.get('participant_id')
            participant = get_object_or_404(ProjectParticipant, id=participant_id, project=project)
            participant.status = 'approved'
            participant.save()
            messages.success(request, f"{participant.worker.get_full_name()} добавлен в проект.")
            return redirect('dashboard:rejected_participants', pk=pk)

        elif 'clear_rejected' in request.POST:
            rejected.delete()
            messages.info(request, "Список отклонённых участников очищен.")
            return redirect('dashboard:rejected_participants', pk=pk)

    return render(request, 'dashboard/projects/participants/rejected_participants.html', {
        'project': project,
        'rejected_participants': rejected
    })


@csrf_exempt
@login_required
def project_participant_profile_api(request, participant_id):
    try:
        participant = ProjectParticipant.objects.select_related('worker').get(id=participant_id)
        user = participant.worker
        data = {
            'full_name': user.get_full_name(),
            'username': user.username,
            'email': user.email,
            'position': user.position,
            'bio': user.bio or '',
            'photo_url': user.profile_picture.url if user.profile_picture else None,
        }

        return JsonResponse(data)
    except ProjectParticipant.DoesNotExist:
        raise Http404("Участник не найден")