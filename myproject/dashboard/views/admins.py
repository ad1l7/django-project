from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from users.models import User
from users.forms import AdminRegisterForm

def is_director(user):
    return user.is_authenticated and user.role == User.DIRECTOR

@user_passes_test(is_director, login_url='users:auth')
def admins_view(request):
    admins = User.objects.filter(role=User.ADMIN)
    form = AdminRegisterForm()

    if request.method == 'POST':
        if 'create_admin' in request.POST:
            form = AdminRegisterForm(request.POST, request.FILES)
            if form.is_valid():
                new_admin = form.save(commit=False)
                new_admin.role = User.ADMIN
                new_admin.save()
                return redirect('dashboard:admins')

        elif 'delete_admin' in request.POST:
            admin_id = request.POST.get('admin_id')
            admin_to_delete = get_object_or_404(User, id=admin_id, role=User.ADMIN)
            admin_to_delete.delete()
            return redirect('dashboard:admins')

        elif 'edit_admin' in request.POST:
            admin_id = request.POST.get('edit_admin')
            admin_to_edit = get_object_or_404(User, id=admin_id, role=User.ADMIN)
            form = AdminRegisterForm(request.POST, request.FILES, instance=admin_to_edit)
            if form.is_valid():
                form.save()
                return redirect('dashboard:admins')

    edit_forms = {adm.id: AdminRegisterForm(instance=adm) for adm in admins}

    return render(request, 'dashboard/admins.html', {
        'admins': admins,
        'form': form,
        'edit_forms': edit_forms,
    })
