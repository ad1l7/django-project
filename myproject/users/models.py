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

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


