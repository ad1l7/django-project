from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm

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
