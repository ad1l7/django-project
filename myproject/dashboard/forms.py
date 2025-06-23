from django import forms
from .models import Project,  ProjectParticipant,ProjectMessage
from .models import Task
from django import forms
from users.models import User
from .models import RewardItem
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'deadline', 'avatar', 'importance', 'description', 'required_workers']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'importance': forms.Select(choices=Project.IMPORTANCE_CHOICES, attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProjectApplicationForm(forms.ModelForm):
    class Meta:
        model = ProjectParticipant
        fields = []

class ProjectMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectMessage
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Введите сообщение...'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'description', 'file', 'reward', 'difficulty']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }

class WorkerEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Оставьте пустым, если не хотите менять пароль"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'profile_picture', 'position', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')

        if new_password:
            # Проверяем, не совпадает ли введённый пароль с текущим
            if not user.check_password(new_password):
                user.set_password(new_password)
            # Иначе ничего не делаем — оставляем старый

        if commit:
            user.save()
        return user
from django import forms
from users.models import User

class AdminEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Оставьте пустым, если не хотите менять пароль"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'profile_picture', 'position', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')

        if new_password:
            if not user.check_password(new_password):
                user.set_password(new_password)

        if commit:
            user.save()
        return user

class RewardItemForm(forms.ModelForm):
    class Meta:
        model = RewardItem
        fields = ['name', 'image', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }