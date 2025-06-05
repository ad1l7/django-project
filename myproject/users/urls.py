from django.urls import path
from .views import auth_view

app_name = 'users'
urlpatterns = [
    path('auth/', auth_view, name='auth'),
]