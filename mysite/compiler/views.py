from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from .models import Directory, File, Section
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import QuerySet
from .forms import UploadFileForm
from django.http import HttpResponseRedirect

import datetime


from django.views import generic

@login_required(login_url="/accounts/login/")
def index(request):
    file = None
    compile_result = None
    compile_result_display = None
    nasm_filename = None
    if request.method == 'POST':
        file_id = request.POST.get('file')
        if file_id != None:
            file = File.objects.get(id=file_id)
        if request.POST.get('remove_section') != None:
            context = {'file': file}
            return render(request, 'compiler/remove-section.html', context)
        content = request.POST.get('content')
        if file and content != None:
            file.update_content(content)
        new_file_id = request.POST.get('new_file')
        if new_file_id != None:
            file = File.objects.get(id=new_file_id)
        if file:
            nasm_filename = file.name[:-1] + 'asm'
        if request.POST.get('compile') != None:
            args = []
            standard = request.POST.get('standard')
            if standard != None:
                args.append(standard)
            processor = request.POST.get('processor')
            args.append(processor)
            if request.POST.get('nogcse'):
                args.append('--nogcse')
            if request.POST.get('noinvariant'):
                args.append('--noinvariant')
            if request.POST.get('noinduction'):
                args.append('--noinduction')
            options = request.POST.get('options')
            if options != None:
                args.append(options)
            compile_result = file.compile(args)
            compile_result_display = file.display_compilation(compile_result)
    if len(request.user.directory_set.all()) == 0:
        d = Directory(name="root", owner=request.user)
        d.save()
    root = request.user.directory_set.all().get(parent = None)
    context = {'root': root, 'file': file, 'compile_result': compile_result, 
               'compile_result_display': compile_result_display, 'nasm_filename': nasm_filename}
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
        if parent != None:
            parent.last_content_change = datetime.datetime.now()
        d = Directory(name=name, parent=parent, owner=request.user)
        d.save()
        parent.save()
        return redirect('compiler:index')
    context = {'directories': request.user.directory_set.all(), 'element': 'katalog'}
    return render (
        request,
        'compiler/new-directory.html',
        context,
    )

def add_file(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent')
        parent = Directory.objects.get(id=parent_id)
        file = request.FILES['file']
        content = file.read().decode('latin-1')
        if parent_id != "":
            parent = Directory.objects.get(id=parent_id)
            parent.last_content_change = datetime.datetime.now()
            f = File(name=file.name, parent=parent, owner=request.user)
            f.save()
            parent.save()
        else:
            f = File(name=file.name, owner=request.user)
            f.save()
        f.update_content(content)
        return redirect('compiler:index')
    context = {'directories': request.user.directory_set.all(), 'element': 'plik'}
    return render (
        request,
        'compiler/new-file.html',
        context,
    )

def remove_directory(request):
    if request.method == 'POST':
        d = Directory.objects.get(id = request.POST.get('id'))
        d.parent.change()
        d.delete()
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
        f.delete()
        f.save()
        return redirect('compiler:index')
    context = {'elements': request.user.file_set.all(), 'element': 'plik'}
    return render (
        request,
        'compiler/remove-element.html',
        context,
    )

def logout_view(request):
    logout(request)
    return redirect('compiler:index')

def remove_section(request):
    if request.method == 'POST':
        section = Section.objects.get(id = request.POST.get('id'))
        section.delete()
        return redirect('compiler:index')
    context = {'sections': File.objects.get(id = request.GET.get('file_id')).section_set.all()}
    return render (
        request,
        'compiler/remove-section.html',
        context,
    )