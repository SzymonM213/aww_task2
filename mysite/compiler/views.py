from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from .models import Directory, File, Section
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import QuerySet

import datetime


from django.views import generic

@login_required(login_url="/accounts/login/")
def index(request):
    if len(request.user.directory_set.all()) == 0:
        d = Directory(name="root", owner=request.user)
        d.save()
    root = request.user.directory_set.all().get(parent = None)
    context = {'root': root}
    return render (
        request,
        'compiler/index.html',
        context,
    )

def add_directory(request):
    if request.method == 'POST':
        name = request.POST.get('element_name')
        parent_id = request.POST.get('parent')
        parent = Directory.objects.get(id=parent_id)
        d = Directory(name=name, parent=parent, owner=request.user)
        d.save()
        parent.save()
        return redirect('compiler:index')
    context = {'directories': request.user.directory_set.all(), 'element': 'katalog'}
    return render (
        request,
        'compiler/new-element.html',
        context,
    )

def add_file(request):
    if request.method == 'POST':
        name = request.POST.get('element_name')
        parent_id = request.POST.get('parent')
        text = request.POST.get('content')
        if parent_id != "":
            parent = Directory.objects.get(id=parent_id)
            f = File(name=name, parent=parent, owner=request.user)
            f.save()
            parent.save()
        else:
            f = File(name=name, owner=request.user)
            f.save()
        sections = Section.split_file(text, f)
        for section in sections:
            section.save()
        return redirect('compiler:index')
    context = {'directories': request.user.directory_set.all(), 'element': 'plik'}
    return render (
        request,
        'compiler/new-element.html',
        context,
    )

def remove_directory(request):
    if request.method == 'POST':
        d = Directory.objects.get(id = request.POST.get('id'))
        d.accessibility = False
        d.last_accessibility_change = datetime.datetime.now()
        d.save()
        return redirect('compiler:index')
    context = {'elements': request.user.directory_set.all(), 'element': 'katalog'}
    return render (
        request,
        'compiler/remove-element.html',
        context,
    )

def remove_file(request):
    if request.method == 'POST':
        f = File.objects.get(id = request.POST.get('id'))
        f.accessibility = False
        f.last_accessibility_change = datetime.datetime.now()
        f.save()
        return redirect('compiler:index')
    context = {'elements': request.user.file_set.all(), 'element': 'katalog'}
    return render (
        request,
        'compiler/remove-element.html',
        context,
    )

def logout_view(request):
    logout(request)
    return redirect('compiler:index')