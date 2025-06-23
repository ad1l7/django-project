from django.urls import path
from .views import auth_view
from .views import profile_view
from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('', views.company_access_view, name='company_access'),
    path('auth/', auth_view, name='auth'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
]