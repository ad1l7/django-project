from django.urls import path
from . import views
from .views import dashboard_view, logout_view, admins_view,workers_view,projects_view, redirect

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_view, name='home'),
    path('logout/', logout_view, name='logout'),
    path('admins/', admins_view, name='admins'),
    path('workers/', workers_view, name='workers'),
    path('projects/', projects_view, name='projects'),
    # Перенаправление /projects/<pk>/ на /projects/<pk>/overview/
    path('projects/<int:pk>/', lambda request, pk: redirect('dashboard:project_overview', pk=pk)),
    path('projects/<int:pk>/overview/', views.project_overview, name='project_overview'),
    path('projects/<int:pk>/chat/', views.project_chat, name='project_chat'),
    path('projects/<int:pk>/participants/', views.project_participants, name='project_participants'),
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('projects/<int:pk>/rejected/', views.rejected_participants, name='rejected_participants'),
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('projects/<int:pk>/access-denied/', views.project_access_denied_custom, name='project_access_denied_custom'),
    path('projects/<int:pk>/tasks/', views.project_tasks, name='project_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]
