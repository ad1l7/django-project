from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm, PasswordForm

def auth_view(request):
    reg_form   = RegisterForm()
    login_form = LoginForm(request=request, data=request.POST or None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
                reg_form = RegisterForm(request.POST)
                if reg_form.is_valid():
                    user = reg_form.save()
                login(request, user)
                return redirect('dashboard:home')
        elif action == 'login':
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('dashboard:home')

    return render(request, 'users/auth.html', {
        'reg_form':    reg_form,
        'login_form':  login_form,
    })
@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=user, user=user)

        password_form = PasswordForm(user, request.POST)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Профиль обновлён.')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён.')
            return redirect('dashboard:profile')

    else:
        profile_form = ProfileForm(instance=user, user=user)
        password_form = PasswordForm(user)

    return render(request, 'dashboard/profile.html', {
        'form': profile_form,
        'pass_form': password_form,
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён.')
        else:
            messages.error(request, 'Ошибка при изменении пароля.')
    return redirect('users:profile')