from django.urls import path
from .views import index

from . import views

app_name = 'compiler'
urlpatterns = [
    path('', index, name='index'),
    path('add-dir/', views.add_directory, name='add_directory'),
    path('add-file/', views.add_file, name='add_file'),
    path('remove-dir/', views.remove_directory, name='remove_directory'),
    path('remove-file/', views.remove_file, name='remove_file'),
    path('logout/', views.logout_view, name='logout'),
    path('remove-section/', views.remove_section, name='remove_section'),
]