from django.urls import path
from .views import index

from . import views

app_name = 'compiler'
urlpatterns = [
    path('', index, name='index'),
    # path('add-dir/', views.add_directory, name='add_directory'),
    # path('add-file/', views.add_file, name='add_file'),
    # path('remove-dir/', views.remove_directory, name='remove_directory'),
    # path('remove-file/', views.remove_file, name='remove_file'),
    path('logout/', views.logout_view, name='logout'),
    # path('remove-section/', views.remove_section, name='remove_section'),
    path('file/<int:file_id>/', views.file, name='file'),
    path('save-file/<int:file_id>/', views.save_file, name='save_file'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete-dir/<int:dir_id>/', views.delete_dir, name='delete_dir'),
    path('create-dir/<int:dir_id>/', views.create_dir, name='create_dir'),
    path('create-file/<int:dir_id>/', views.create_file, name='create_file'),
    path('compile/<int:file_id>/', views.compile_file, name='compile'),
    path('register/', views.register, name='register'),
]