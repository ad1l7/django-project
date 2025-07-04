# Generated by Django 5.2.1 on 2025-06-07 22:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_personaltask_options_personaltask_color_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='personaltask',
            options={},
        ),
        migrations.RemoveField(
            model_name='personaltask',
            name='color',
        ),
        migrations.RemoveField(
            model_name='personaltask',
            name='order',
        ),
        migrations.AlterField(
            model_name='personaltask',
            name='status',
            field=models.CharField(choices=[('todo', 'Задачи'), ('in_progress', 'В процессе'), ('done', 'Завершено')], default='todo', max_length=20),
        ),
        migrations.AlterField(
            model_name='personaltask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
