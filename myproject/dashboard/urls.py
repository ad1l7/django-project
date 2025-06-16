from django.urls import path
from . import views
from .views import (
    dashboard_view, logout_view, admins_view, workers_view,
    projects_view, redirect, statistics
)
from dashboard.views.project_chat import fetch_project_messages
app_name = 'dashboard'

urlpatterns = [
    # Главная и профиль
    path('', dashboard_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),

    # Персональные задачи (Kanban)
    path('add/', views.add_task, name='add_task'),
    path('update/', views.update_task_status, name='update_task_status'),
    path('personal/delete-task/', views.delete_personal_task, name='delete_personal_task'),

    # Управление пользователями
    path('admins/', admins_view, name='admins'),
    path('workers/', workers_view, name='workers'),

    # Проекты — список и редирект
    path('projects/', projects_view, name='projects'),
    path('projects/<int:pk>/', lambda request, pk: redirect('dashboard:project_overview', pk=pk)),

    # Проекты — доступ и детали
    path('projects/<int:pk>/overview/', views.project_overview, name='project_overview'),
    path('projects/<int:pk>/access-denied/', views.project_access_denied_custom, name='project_access_denied_custom'),
    path('projects/<int:pk>/participants/', views.project_participants, name='project_participants'),
    path('projects/<int:pk>/rejected/', views.rejected_participants, name='rejected_participants'),
    path('projects/<int:pk>/chat/', views.project_chat, name='project_chat'),
    path('projects/<int:pk>/chat/fetch/', fetch_project_messages, name='fetch_project_messages'),
    path('projects/<int:pk>/tasks/', views.project_tasks, name='project_tasks'),
    path('projects/<int:pk>/my-tasks/', views.my_tasks_view, name='my_tasks'),
    path('projects/<int:pk>/submitted-tasks/', views.submitted_tasks_view, name='submitted_tasks'),
    path('projects/<int:pk>/completed-tasks/', views.completed_tasks_view, name='completed_tasks'),
    path('api/participants/<int:participant_id>/profile/', views.project_participant_profile_api, name='participant_profile_api'),
    path('projects/<int:pk>/statistics/', statistics, name='statistics'),
    # Задачи
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/take/', views.take_task, name='take_task'),
    path('tasks/<int:task_id>/drop/', views.drop_task, name='drop_task'),
    path('tasks/<int:task_id>/submit/', views.submit_task, name='submit_task'),
    path('tasks/<int:task_id>/approve/', views.approve_task, name='approve_task'),
    path('tasks/<int:task_id>/reject/', views.reject_task, name='reject_task'),

    # Рейтинг
    path('rating/', views.rating_view, name='rating'),
    path('rating/reset/', views.reset_rewards, name='reset_rewards'),
]
