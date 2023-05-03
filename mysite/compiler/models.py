from django.db import models
from datetime import date

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
    # description = models.CharField(max_length=200, null=True)
    # date_created = models.DateTimeField(default = date.today)
    # # owner = models.ForeignKey('auth.User', related_name='elements', on_delete=models.CASCADE)
    # accessibility = models.BooleanField(default=True)
    # last_accessibility_change = models.DateTimeField(default = None, null=True)
    # last_content_change = models.DateTimeField(default = None, null=True)

    def tree(self):
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
    file = models.ForeignKey('File', on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(max_length=200, default=None, null=True)
    description = models.CharField(max_length=200, default=None, null=True)
    date_created = models.DateTimeField(default = date.today)
    begin = models.IntegerField(default=None, null=True)
    end = models.IntegerField(default=None, null=True)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=None, null=True)
    text = models.CharField(max_length=2000)

class File(models.Model):
    name = models.CharField(max_length=200, default=None, null=True)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, default=None, null=True)

    def tree(self):
        return '<li class="file">' + self.name + "</li>"
    
    def content(self):
        result = ''
        for section in self.section_set.all():
            result += section.text + '\n'
        return result