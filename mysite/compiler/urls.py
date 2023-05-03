from django.urls import path
from .views import index

from . import views

app_name = 'compiler'
urlpatterns = [
    path('', index, name='index'),
    path('add-dir/', views.add_directory, name='add_directory'),
    path('add-file/', views.add_file, name='add_file'),
]