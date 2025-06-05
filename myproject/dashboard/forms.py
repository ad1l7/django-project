from django import forms
from .models import Project,  ProjectParticipant,ProjectMessage
from .models import Task
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
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Введите сообщение...'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'description', 'file', 'reward']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
