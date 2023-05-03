from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from .models import Directory, File

from django.views import generic

def index(request):
    context = {'directories': Directory.objects.all()}
    return render (
        request,
        'compiler/index.html',
        context,
    )

def add_directory(request):
    print("add_directory")
    if request.method == 'POST':
        name = request.POST.get('element_name')
        parent_id = request.POST.get('parent')
        if parent_id != None:
            parent = Directory.objects.get(id=parent_id)
            d = Directory(name=name, parent=parent)
            d.save()
            parent.save()
        else:
            d = Directory(name=name)
            d.save()
        return redirect('compiler:index')
    context = {'directories': Directory.objects.all(), 'element': 'katalog'}
    return render (
        request,
        'compiler/new-element.html',
        context,
    )

def add_file(request):
    print("add_file")
    if request.method == 'POST':
        name = request.POST.get('element_name')
        parent_id = request.POST.get('parent')
        if parent_id != None:
            parent = Directory.objects.get(id=parent_id)
            f = File(name=name, parent=parent)
            f.save()
            parent.save()
        else:
            f = File(name=name)
            f.save()
        return redirect('compiler:index')
    context = {'directories': Directory.objects.all(), 'element': 'plik'}
    return render (
        request,
        'compiler/new-element.html',
        context,
    )
