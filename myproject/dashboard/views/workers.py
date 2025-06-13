from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from users.models import User
from users.forms import WorkerRegisterForm
from dashboard.forms import WorkerEditForm


def is_director_or_admin(user):
    return user.is_authenticated and user.role in (User.DIRECTOR, User.ADMIN)

@user_passes_test(is_director_or_admin, login_url='users:auth')
def workers_view(request):
    workers = User.objects.filter(role=User.WORKER)
    form = WorkerRegisterForm()

    if request.method == 'POST':
        if 'create_worker' in request.POST:
            form = WorkerRegisterForm(request.POST, request.FILES)
            if form.is_valid():
                worker = form.save(commit=False)
                worker.role = User.WORKER
                worker.set_password(form.cleaned_data['password'])  # шифруем пароль
                worker.save()
                return redirect('dashboard:workers')

        elif 'delete_worker' in request.POST:
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(User, id=worker_id, role=User.WORKER)
            worker.delete()
            return redirect('dashboard:workers')

        elif 'edit_worker' in request.POST:
            worker_id = request.POST.get('edit_worker')
            worker = get_object_or_404(User, id=worker_id, role=User.WORKER)
            form = WorkerEditForm(request.POST, request.FILES, instance=worker)
            if form.is_valid():
                worker = form.save(commit=False)
                password = form.cleaned_data.get('password')
                if password:
                    worker.set_password(password)  # шифруем новый пароль
                worker.save()
                return redirect('dashboard:workers')

    edit_forms = {w.id: WorkerEditForm(instance=w) for w in workers}

    return render(request, 'dashboard/workers/workers.html', {
        'workers': workers,
        'form': form,
        'edit_forms': edit_forms,
    })