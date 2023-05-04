from django.db import models
from datetime import date
from django.contrib.auth.models import User
import re

# Create your models here.
# class Element(models.Model):    
#     name = models.CharField(max_length=200)
#     directory = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
#     # description = models.CharField(max_length=200, blank=True)
#     # date_created = models.DateTimeField(default = date.today)
#     # owner = models.ForeignKey('auth.User', related_name='elements', on_delete=models.CASCADE)
#     # accessibility = models.BooleanField(default=True)
#     # last_accessibility_change = models.DateTimeField(default = None)
#     # last_content_change = models.DateTimeField(default = None)

class Directory(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(default = date.today)
    accessibility = models.BooleanField(default=True)
    last_accessibility_change = models.DateTimeField(default = None, null=True)
    last_content_change = models.DateTimeField(default = None, null=True)

    def root(self):
        result = ''
        for element in self.directory_set.all():
                result += element.tree()
        for element in self.file_set.all():
            result += element.tree()
        return result

    def tree(self):
        if not self.accessibility:
            return ""
        result = '<li class="directory">' + '<details><summary>' + self.name.replace('<', '&lt;').replace('>', '&gt;') + '</summary>'
        if self.directory_set != []:
            result += '<ul>'
            for element in self.directory_set.all():
                result += element.tree()
            for element in self.file_set.all():
                result += element.tree()
            result += '</ul>'
        result += '</details>'
        result += '</li>'
        return result
    
class Section(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    file = models.ForeignKey('File', on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(max_length=200, default=None, null=True)
    description = models.CharField(max_length=200, default=None, null=True)
    date_created = models.DateTimeField(default = date.today)
    begin = models.IntegerField(default=None, null=True)
    end = models.IntegerField(default=None, null=True)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=None, null=True)
    text = models.CharField(max_length=2000)

    # returns list of automatically generated sections
    @staticmethod
    def split_file(text, file):
        proc_pattern = r'\bvoid\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{[^{}]*({[^{}]*}[^{}]*?)*}'
        comment_pattern = r'\/\/[^\n]*|\/\*[\s\S]*?\*\/'
        directive_pattern = r'#\s*\w+.*'
        var_pattern = r'\b(int|float|double|char|short|long|unsigned|signed|void)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*(\[\s*\d*\s*\])*\s*;'
        asm_pattern = r'.*__asm__.*'
        result = []
        current_section_text = ''
        current_begin = 0
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            if re.search(proc_pattern, lines[i]):
                current_begin = i
                while i < len(lines) and re.search(proc_pattern, lines[i]):
                    current_section_text += lines[i]
                    i += 1
                result.append(Section(text=current_section_text, type='procedure', begin=current_begin, end=i-1, file=file))
                current_section_text = ''
            elif re.search(comment_pattern, lines[i]):
                current_begin = i
                while i < len(lines) and re.search(comment_pattern, lines[i]):
                    current_section_text += lines[i]
                    i += 1
                result.append(Section(text=current_section_text, type='comment', begin=current_begin, end=i-1, file=file))
                current_section_text = ''
            elif re.search(directive_pattern, lines[i]):
                current_begin = i
                while i < len(lines) and re.search(directive_pattern, lines[i]):
                    current_section_text += lines[i]
                    i += 1
                result.append(Section(text=current_section_text, type='directive', begin=current_begin, end=i-1, file=file))
                current_section_text = ''
            elif re.search(var_pattern, lines[i]):
                current_begin = i
                while i < len(lines) and re.search(var_pattern, lines[i]):
                    current_section_text += lines[i]
                    i += 1
                result.append(Section(text=current_section_text, type='variable', begin=current_begin, end=i-1, file=file))
                current_section_text = ''
            elif re.search(asm_pattern, lines[i]):
                current_begin = i
                while i < len(lines) and re.search(asm_pattern, lines[i]):
                    current_section_text += lines[i]
                    i += 1
                result.append(Section(text=current_section_text, type='asm', begin=current_begin, end=i-1, file=file))
                current_section_text = ''
            else:
                result.append(Section(text=lines[i], type='undifined', begin=i, end=i, file=file))
                i += 1
        return result

class File(models.Model):
    name = models.CharField(max_length=200, default=None, null=True)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, default=None, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(default = date.today)
    accessibility = models.BooleanField(default=True)
    last_accessibility_change = models.DateTimeField(default = None, null=True)
    last_content_change = models.DateTimeField(default = None, null=True)

    def tree(self):
        if self.accessibility:
            return '<li><button class="file" type="submit" name="file" value="' + str(self.id) + '">' + self.name + '</button></li>'
        else:
            return ""
        
    
    def content(self):
        result = ''
        for section in self.section_set.all():
            result += section.text
        return result