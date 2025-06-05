from django.db import models
from users.models import User
from django.conf import settings
from django.utils import timezone
# Create your models here.
class Project(models.Model):
    IMPORTANCE_CHOICES = [
        ('low', 'Низкий приоритет'),
        ('medium', 'Средний приоритет'),
        ('high', 'Высокий приоритет'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    deadline = models.DateField(verbose_name='Дедлайн')
    avatar = models.ImageField(upload_to='projects/avatars/', verbose_name='Аватарка', blank=True, null=True)
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, verbose_name='Важность')
    description = models.TextField(verbose_name='Описание')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    required_workers = models.PositiveIntegerField(verbose_name='Количество работников')

    def __str__(self):
        return self.title


class ProjectParticipant(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Заявка подана'),
        ('invited', 'Приглашён'),
        ('approved', 'Утверждён'),
        ('rejected', 'Отклонён'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='participants')
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='applied')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'worker')

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.project.title} ({self.get_status_display()})"
    

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.get_full_name()} ({self.timestamp}): {self.content}"


class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    file = models.FileField(upload_to='task_files/', blank=True, null=True)
    reward = models.PositiveIntegerField(default=0) 
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title