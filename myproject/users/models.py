from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    DIRECTOR = 'DIRECTOR'
    ADMIN = 'ADMIN'
    WORKER = 'WORKER'
    ROLE_CHOICES = [
        (DIRECTOR, 'Директор'),
        (ADMIN, 'Администратор'),
        (WORKER, 'Работник'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='Роль'
    )

    # 🟢 Добавляем эти поля:
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name="Фото профиля")
    bio = models.TextField(null=True, blank=True, verbose_name="Описание")
    position = models.CharField(max_length=255, null=True, blank=True, verbose_name="Должность")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"