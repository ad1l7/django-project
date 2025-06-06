from urllib import request
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from .models import User
class RegisterForm(forms.ModelForm):
    password   = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Имя'
    )
    last_name  = forms.CharField(
        max_length=150,
        required=True,
        label='Фамилия'
    )
    username   = forms.CharField(
        max_length=150,
        required=True,
        label='Имя пользователя'
    )
    email      = forms.EmailField(
        required=True,
        label='Email'
    )

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap-классы для всех полей
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        user.role     = User.WORKER  # Все новые — Работники
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='Роль',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap-классы для username и password
        for name, field in self.fields.items():
            if name in ('username', 'password'):
                field.widget.attrs.update({'class': 'form-control'})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        selected = self.cleaned_data.get('role')
        if user.role != selected:
            raise forms.ValidationError("Неправильная роль для данного пользователя.")
class AdminRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.ADMIN
        if commit:
            user.save()
        return user
    
class WorkerRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.WORKER
        if commit:
            user.save()
        return user
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'profile_picture', 'position']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Работникам нельзя менять email и должность
        if user and user.role == 'WORKER':
            self.fields.pop('position')
            self.fields.pop('email')

class PasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )