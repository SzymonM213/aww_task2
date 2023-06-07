from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from .models import Directory, File, Section
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import QuerySet
from .forms import UploadFileForm
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


import datetime


from django.views import generic

@login_required(login_url="/accounts/login/")
def index(request):
    if len(request.user.directory_set.all()) == 0:
        d = Directory(name="root", owner=request.user)
        d.save()
    root = request.user.directory_set.all().get(parent = None)
    context = {"root": root, "file": file}
    return render (
        request,
        'compiler/index.html',
        context,
    )

def logout_view(request):
    logout(request)
    return redirect('compiler:index')

def file(request, file_id):
    if file_id < 0:
        return JsonResponse({'success': False})
    file = File.objects.get(id=file_id)
    file_data = {
        'name': file.path(),
        'content': file.content(),
        'success': True,
    }
    return JsonResponse(file_data)

@csrf_exempt
def save_file(request, file_id):
    file = File.objects.get(id=file_id)
    content = json.loads(request.body).get('content', '')
    print("content:", content)
    file.update_content(content)
    return JsonResponse({'success': True})

@csrf_exempt
def create_dir(request, dir_id):
    if dir_id == 0:
        parent = request.user.directory_set.all().get(parent = None)
    else:
        parent = Directory.objects.get(id=dir_id)
    if json.loads(request.body):
        name = json.loads(request.body).get('name', '')
    else:
        name = "New directory"
    d = Directory(name=name, parent=parent, owner=request.user)
    d.save()
    print("chuj")
    data = {'success': True, 'id': d.id}
    return JsonResponse(data)

@csrf_exempt
def create_file(request, dir_id):
    if dir_id == 0:
        parent = request.user.directory_set.all().get(parent = None)
    else:
        parent = Directory.objects.get(id=dir_id)
    name = json.loads(request.body).get('name', '')
    content = json.loads(request.body).get('content', '')
    f = File(name=name, parent=parent, owner=request.user)
    f.save()
    print("chuj" + str(dir_id))
    f.update_content(content)
    data = {'success': True, 'id': f.id}
    return JsonResponse(data)

@csrf_exempt
def delete_file(request, file_id):
    file = File.objects.get(id=file_id)
    if file == None:
        return JsonResponse({'success': False})
    file.delete()
    file.save()
    return JsonResponse({'success': True})

@csrf_exempt
def delete_dir(request, dir_id):
    dir = Directory.objects.get(id=dir_id)
    if dir == None:
        return JsonResponse({'success': False})
    dir.delete()
    dir.save()
    return JsonResponse({'success': True})

@csrf_exempt
def compile_file(request, file_id):
    file = File.objects.get(id=file_id)
    compile_result = file.compile([])
    compile_result_display = file.display_compilation(compile_result)
    return JsonResponse({'success': True, 'result': compile_result, 'result_display': compile_result_display, 'file_name': file.name})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            return render(request, 'compiler/register.html', {'error': 'Hasła nie są takie same'})
        if User.objects.filter(username=username).exists():
            return render(request, 'compiler/register.html', {'error': 'Użytkownik o takiej nazwie już istnieje'})
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('compiler:index')
    return render(request, 'compiler/register.html')

