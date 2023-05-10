from django.db import models
from datetime import date
from django.contrib.auth.models import User
import re
import subprocess
import os
from datetime import datetime
from django.utils import timezone

class Directory(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now=True)
    access = models.BooleanField(default=True)
    last_access_change = models.DateTimeField(default = None, null=True)
    last_content_change = models.DateTimeField(default = None, null=True)

    def root(self):
        result = ''
        for element in self.directory_set.all():
                result += element.tree()
        for element in self.file_set.all():
            result += element.tree()
        return result

    def tree(self):
        if not self.access:
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
    
    def path(self):
        if self.parent.parent == None:
            return self.name
        return self.parent.path() + "/" + self.name
    
    def delete(self):
        self.access = False
        self.last_access_change = timezone.now()
        for dir in self.directory_set.all():
            dir.delete()
        for file in self.file_set.all():
            file.delete()

    def change(self):
        self.last_content_change = timezone.now
    
class Section(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    file = models.ForeignKey('File', on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(max_length=200, default=None, null=True)
    description = models.CharField(max_length=200, default=None, null=True)
    date_created = models.DateTimeField(auto_now=True)
    begin = models.IntegerField(default=None)
    end = models.IntegerField(default=None)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default="no warnings", null=True)
    status_data = models.CharField(max_length=200, default=None, null=True)
    text = models.CharField(max_length=2000)

    # returns list of automatically generated sections
    @staticmethod
    def split_file(text, file):
        directive_pattern = r'#\s*\w+.*'
        var_pattern = r'\b(int|float|double|char|short|long|unsigned|signed)\b'
        asm_pattern = '__asm'
        asm_end_pattern = '__endasm'
        result = []
        current_section_text = ''
        current_begin = 0
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            if lines[i][0:2] ==  "//":
                current_begin = i+1
                while i < len(lines) and lines[i][0:2] ==  "//":
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='comment', begin=current_begin, end=i, file=file))
                current_section_text = ''
            elif lines[i][0:2] ==  "/*":
                current_begin = i
                while i < len(lines) and "*/" not in lines[i-1]:
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='comment', begin=current_begin, end=i+1, file=file))
                current_section_text = ''
            elif 'void ' in lines[i] or lines[i] == "{":
                current_begin = i+1
                result.append(Section(text=lines[i] + '\n', type='procedure', begin=current_begin, end=i+1, file=file))
                current_section_text = ''
                i += 1
            elif re.search(directive_pattern, lines[i]):
                current_begin = i+1
                while i < len(lines) and re.search(directive_pattern, lines[i]):
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='directive', begin=current_begin, end=i, file=file))
                current_section_text = ''
            elif re.search(var_pattern, lines[i]):
                current_begin = i+1
                count = 0
                while i < len(lines) and re.search(var_pattern, lines[i]):
                    count +=1
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='variable', begin=current_begin, end=i, file=file))
                current_section_text = ''
            elif asm_pattern in lines[i]:
                current_begin = i+1
                while i < len(lines) and asm_end_pattern not in lines[i - 1]:
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='asm', begin=current_begin, end=i, file=file))
                current_section_text = ''
            elif lines[i].isspace() or lines[i] == '':
                current_begin = i+1
                while i < len(lines) and (lines[i].isspace() or lines[i] == ''):
                    current_section_text += lines[i] + '\n'
                    i += 1
                result.append(Section(text=current_section_text, type='whitespace', begin=current_begin, end=i, file=file))
                current_section_text = ''
            else:
                result.append(Section(text=lines[i] + '\n', type='undefined', begin=i+1, end=i+1, file=file))
                i += 1
        return result
    
    def error(self):
        return self.status == 'error'
    
    def warning(self):
        return self.status == 'warning'

class File(models.Model):
    name = models.CharField(max_length=200, default=None, null=True)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, default=None, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now=True)
    access = models.BooleanField(default=True)
    last_access_change = models.DateTimeField(default = None, null=True)
    last_content_change = models.DateTimeField(default = None, null=True)

    def tree(self):
        if self.access:
            return '<li><button class="file" type="submit" name="new_file" value="' + str(self.id) + '">' + self.name.replace('<', '&lt;').replace('>', '&gt;') + '</button></li>'
        else:
            return ""
    
    def content(self):
        result = ''
        for section in self.section_set.all():
            result += section.text
        return result
    
    def path(self):
        if self.parent.parent == None:
            return self.name
        return self.parent.path() + "/" + self.name
    
    def update_content(self, text):
        text = text.replace('\r', '')
        sections = Section.split_file(text, self)
        self.last_content_change = datetime.now()
        self.section_set.all().delete()
        for section in sections:
            section.save()

    def compile(self, args):
        f = open(str(self.id) + '.c', 'w+')
        f.write(self.content())
        f.close()
        command = ["sdcc", "-S"]
        result = ''
        p = subprocess.run(command + args + [f'{self.id}.c'], capture_output=True)
        errors = p.stderr.decode('utf-8').splitlines()
        for error in errors:
            if ":" not in error:
                continue
            if "warning" in error:
                error_details = error.split(':')[1]
                line_number = int(error_details.split(':')[0])
                for section in self.section_set.all():
                    if line_number >= section.begin and line_number <= section.end and section.status != "error":
                        section.status = "warning"
                        section.status_data = error_details
                        section.save()
            if "error" in error:
                error_details = error.split(':')[1]
                line_number = int(error_details.split(':')[0])
                for section in self.section_set.all():
                    if line_number >= section.begin and line_number <= section.end:
                        section.status = "error"
                        section.status_data = error_details
                        section.save()
        os.remove(str(self.id) + '.c')
        if os.path.isfile(str(self.id) + '.asm') and p.returncode == 0:
            f = open(str(self.id) + '.asm', 'r')
            result = f.read()
            f.close()
            os.remove(str(self.id) + '.asm')
            return result
        return 'error'
    
    def display_compilation(self, text):
        first_line = 1
        text = text.splitlines()
        result = ""
        for line in text:
            if line == ";--------------------------------------------------------":
                if first_line:
                    if result != "":
                        result += "</div>"
                    result += "<div class='asm-section'>"
                    result += "<div class='asm-section-header'>"
                    result += line + '\n'
                    first_line = 0
                else:
                    result += line + '\n'
                    result += "</div>"
                    first_line = 1
            else:
                result += line + '\n'
        if "<div" in result:
            return result + "</div>"
        else:
            return result
    
    def delete(self):
        self.access = False
        self.last_access_change = timezone.now()

    def debug(self):
        for section in self.section_set.all():
            if section.status == 'error':
                return "git"
            if section.status == 'warning':
                return "git"
        return "niegit"
