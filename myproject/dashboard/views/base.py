import json
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from users.forms import ProfileForm
from dashboard.models import PersonalTask

@login_required
def dashboard_view(request):
    tasks = PersonalTask.objects.filter(user=request.user)
    return render(request, 'dashboard/dashboard.html', {'tasks': tasks})

def logout_view(request):
    logout(request)
    return redirect('users:auth')

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
