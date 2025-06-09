from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.timezone import now, timedelta
from users.models import User
from dashboard.models import Task

@login_required
def rating_view(request):
    filter_type = request.GET.get('filter', 'month')
    all_users = User.objects.all()

    if filter_type == 'day':
        since = now().date() - timedelta(days=1)
    elif filter_type == 'week':
        since = now().date() - timedelta(days=7)
    else:
        since = now().date() - timedelta(days=30)

    done_tasks = Task.objects.filter(status='done', created_at__date__gte=since)

    rewards_dict = {}
    for task in done_tasks:
        if task.assigned_to_id:
            rewards_dict[task.assigned_to_id] = rewards_dict.get(task.assigned_to_id, 0) + task.reward

    user_rewards = []
    for user in all_users:
        reward = rewards_dict.get(user.id, 0)

        if user.role == 'WORKER':
            role_label = '👷 Работник'
        elif user.role == 'ADMIN':
            role_label = '🧑‍💼 Админ'
        elif user.role == 'DIRECTOR':
            role_label = '👨‍💼 Директор'
        else:
            role_label = 'Пользователь'

        user_rewards.append({
            'user': user,
            'reward': reward,
            'role_label': role_label
        })

    user_rewards.sort(key=lambda x: x['reward'], reverse=True)

    return render(request, 'dashboard/rating/rating.html', {
        'user_rewards': user_rewards,
        'filter': filter_type
    })


@user_passes_test(lambda u: u.is_authenticated and u.role in ('ADMIN', 'DIRECTOR'))
def reset_rewards(request):
    if request.method == 'POST':
        User.objects.all().update(total_reward=0)
        Task.objects.filter(status='done').update(reward=0)
        messages.success(request, 'Награды успешно обнулены, задачи сохранены.')
    return redirect('dashboard:rating')
