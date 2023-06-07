from django.test import TestCase

from .models import Directory, File, Section
from django.contrib.auth.models import User
from . import views
from django.http import JsonResponse
import json
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.test import TestCase, Client

class DirectoryModelTests(TestCase):

    def test_directory_creation(self):
        """
        Tests that a directory can be created.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        directory = Directory(name='testdir', owner=user)
        directory.save()
        self.assertEqual(directory.name, 'testdir')
        self.assertEqual(directory.owner, user)
        self.assertEqual(directory.parent, None)
    
    def test_path_structure(self):
        """
        Tests that a directory with a parent displays proper path.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        root = Directory(name='root', owner=user)
        root.save()
        parent = Directory(name='parent', owner=user, parent=root)
        parent.save()
        child = Directory(name='child', owner=user, parent=parent)
        child.save()
        self.assertEqual(child.path(), 'parent/child')

    def test_deletion(self):
        """
        Tests that a directory can be deleted.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        directory = Directory(name='testdir', owner=user)
        directory.save()
        file = File(name='testfile', owner=user, parent=directory)
        file.save()
        self.assertEqual(directory.access, True)
        self.assertEqual(file.access, True)
        directory.delete()
        self.assertEqual(directory.access, False)

    def test_tree(self):
        """
        Tests that a directory can be displayed as a tree.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        root = Directory(name='root', owner=user)
        root.save()
        parent = Directory(name='parent', owner=user, parent=root)
        parent.save()
        child = Directory(name='child', owner=user, parent=parent)
        child.save()
        self.assertTrue("root" in root.tree())
        self.assertTrue("parent" in root.tree())
        self.assertTrue("child" in root.tree())

        # tree after deletion
        root.delete()
        self.assertEqual(root.tree(), '')

    def test_root(self):
        user = User.objects.create_user('testuser', 'testpswd')
        root = Directory(name='root', owner=user)
        root.save()
        parent = Directory(name='parent', owner=user, parent=root)
        parent.save()
        file = File(name='testfile', owner=user, parent=root)
        file.save()
        self.assertTrue('testfile' in root.root())
        self.assertTrue('parent' in root.root())

class FileModelTests(TestCase):
     
    def test_update_content(self):
        """
        Tests that a file can be created and its content can be updated.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        directory = Directory(name='testdir', owner=user)
        directory.save()
        file = File(name='testfile', owner=user, parent=directory)
        file.save()
        self.assertEqual(file.content(), '')
        file.update_content('testcontent')
        self.assertEqual(file.content(), 'testcontent\n')

    def test_deletion(self):
        """
        Tests that a file can be deleted.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        directory = Directory(name='testdir', owner=user)
        directory.save()
        file = File(name='testfile', owner=user, parent=directory)
        file.save()
        self.assertEqual(file.access, True)
        file.delete()
        self.assertEqual(file.access, False)
    
    def test_path_structure(self):
        """
        Tests that a file with a parent displays proper path.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        root = Directory(name='root', owner=user)
        root.save()
        parent = Directory(name='parent', owner=user, parent=root)
        parent.save()
        file = File(name='testfile', owner=user, parent=parent)
        file.save()
        self.assertEqual(file.path(), 'parent/testfile')
        
    def test_deleted_file_tree(self):
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        file.delete()
        self.assertEqual(file.tree(), '')

class SectionModelTests(TestCase):

    def test_add_section(self):
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        file.update_content('testcontent')
        section = Section(file=file, begin=0, end=4)
        section.save()
        self.assertEqual(section.file, file)
        self.assertEqual(section.begin, 0)
        self.assertEqual(section.end, 4)

    def test_split_file(self):
        text = """
            #include <stdio.h>
            #include <stdlib.h>

            // function bad()
            int bad() {
                return "42";
            }

            /* 
                blad2 
                lol   
            */
            int blad2 = "lol";

            int main() {
                return 5;
            }

            void foo() {
                return;
            }
        """
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        sections = Section.split_file(text, file)
        self.assertEqual(len(sections), 22)
        self.assertEqual(sections[0].begin, 1)
        self.assertEqual(sections[0].end, 1)
        self.assertEqual(sections[1].begin, 2)
        self.assertEqual(sections[1].end, 3)
        self.assertEqual(sections[3].type, 'undefined')
        self.assertEqual(sections[4].type, 'variable')
        self.assertEqual(sections[7].type, 'whitespace')

    def test_asm_section(self):
        text = """
            __asm
            {
                mov eax, 0x0
                mov ebx, 0x1
                mov ecx, 0x2
                mov edx, 0x3
            }
            """
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        sections = Section.split_file(text, file)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[1].type, 'asm')

    def test_error(self):
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        section = Section(file=file, begin=0, end=4)
        section.status = 'error'
        section.save()
        self.assertEqual(section.error(), True)

class FileSectionTest(TestCase):

    def test_create_file(self):
        """
        Tests that a file can be created and split into sections.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        text = """#include <stdio.h>\n#include <stdlib.h>\nint main() {\nreturn 0;\n}"""
        file.update_content(text)
        self.assertEqual(len(Section.objects.all()), 4)
        self.assertEqual(file.content(), text + '\n')

    def test_compile(self):
        """
        Tests that a file can be compiled.
        """
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        text = """#include <stdio.h>\n#include <stdlib.h>\nint main() {\nchuj\nreturn 0;\n}"""
        file.update_content(text)
        file.compile([])
        section = Section.objects.get(begin=5)
        self.assertEqual(section.status, 'error')
        
    def test_display_compilation(self):
        user = User.objects.create_user('testuser', 'testpswd')
        file = File(name='testfile', owner=user)
        file.save()
        text = """#include <stdio.h>\n#include <stdlib.h>\nint main() {\nchuj\nreturn 0;\n}"""
        file.update_content(text)
        compilation = file.compile([])
        self.assertTrue("error" in file.display_compilation(compilation))

class ViewTest(TestCase):
    
    def test_file(self):
        user = User.objects.create_user('testuser', 'testpswd')
        parent = Directory(name='testdir', owner=user)
        parent.save()
        file = File(name='testfile', owner = user, parent=parent)
        file.save()
        file.update_content('testcontent')
        response = views.file(None, file.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['content'], 'testcontent\n')
        self.assertEqual(json.loads(response.content)['name'], 'testfile')

    def test_delete_file(self):
        user = User.objects.create_user('testuser', 'testpswd')
        parent = Directory(name='testdir', owner=user)
        parent.save()
        file = File(name='testfile', owner = user, parent=parent)
        file.save()
        response = views.delete_file(None, file.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)

    def test_delete_dir(self):
        user = User.objects.create_user('testuser', 'testpswd')
        parent = Directory(name='testdir', owner=user)
        parent.save()
        dir = Directory(name='testdir', owner = user, parent=parent)
        dir.save()
        response = views.delete_dir(None, dir.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)

    def test_wrong_data(self):
        user = User.objects.create_user('testuser', 'testpswd')
        parent = Directory(name='testdir', owner=user)
        parent.save()
        file = File(name='testfile', owner = user, parent=parent)
        file.save()
        response = views.file(None, -1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_index(self):
        self.user = User.objects.create_user('testuser', 'testpswd')
        self.client.login(username='testuser', password='testpswd')
        self.factory = RequestFactory()
        request = self.factory.get(reverse('compiler:index'))
        request.user = self.user
        response = views.index(request)
        self.assertEqual(response.status_code, 200)

    def test_save_file(self):
        self.client = Client()
        user = User.objects.create_user('testuser', 'testpswd')
        self.file = File.objects.create(id=1, owner = user)

        # Prepare test data
        file_id = self.file.id
        content = 'Sample content'

        # Create a POST request with JSON data
        data = {'content': content}
        response = self.client.post(f'/compiler/save-file/{file_id}/', data=json.dumps(data), content_type='application/json')

        # Assert response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'success': True})

    # def test_create_dir(self):
    #     self.client = Client()
    #     user = User.objects.create_user('testuser', 'testpswd')
    #     user.save()

    #     print(User.objects.all())

    #     # Prepare test data
    #     name = 'Sample name'
    #     parent = Directory.objects.create(owner = user)

    #     # Create a POST request with JSON data
    #     data = {'name': name}

    #     logged_in = self.client.login(username='testuser', password='testpswd')
    #     self.assertTrue(logged_in)

    #     response = self.client.post(f'/compiler/create-dir/{parent.id}/', data=json.dumps(data), content_type='application/json')

    #     # Assert response status code and content
    #     self.assertEqual(response.status_code, 200)
    #     self.assertDictEqual(response.json(), {'success': True})

    def test_create_dir(self):
        user = User.objects.create_user('testuser', 'testpswd')

        parent = Directory.objects.create(name='testdir', owner=user)
        parent.save()

        factory = RequestFactory()
        request = factory.post(f'/compiler/create-dir/{parent.id}/', content = {'name': 'testdir'}, content_type='application/json')
        request.user = user
        response = views.create_dir(request, parent.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)

    def test_create_file(self):
        user = User.objects.create_user('testuser', 'testpswd')

        parent = Directory.objects.create(name='testdir', owner=user)
        parent.save()

        factory = RequestFactory()
        request = factory.post(f'/compiler/create-file/{parent.id}/', content = {'name': 'testfile'}, content_type='application/json')
        request.user = user
        response = views.create_file(request, parent.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)

    def test_compile_file(self):
        user = User.objects.create_user('testuser', 'testpswd')

        parent = Directory.objects.create(name='testdir', owner=user)
        parent.save()

        file = File.objects.create(name='testfile', owner=user, parent=parent)
        file.save()

        factory = RequestFactory()
        request = factory.post(f'/compiler/compile-file/{file.id}/', content = {'name': 'testfile'}, content_type='application/json')
        request.user = user
        response = views.compile_file(request, file.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)

    def test_register(self):
        response = self.client.post('/compiler/register/', {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect response


# from django.urls import reverse
# from django.contrib.auth import get_user

# class LogoutViewTestCase(TestCase):

#     def test_logout_view(self):
#         self.client.login(username='testuser', password='testpass')
#         self.factory = RequestFactory()


#         url = reverse('compiler:index')  # Replace 'compiler:index' with the actual URL pattern name

#         self.assertTrue(get_user(self.client).is_authenticated)

from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse

class FileViewTestCase(TestCase):
    def test_file_view_with_valid_id(self):
        # Create a file for testing
        self.user = User.objects.create_user(username='testuser', password='testpass')
        file = File.objects.create(name='testfile.txt', owner=self.user)

        response = self.client.get(f"/compiler/file/{file.id}")

        self.assertEqual(response.status_code, 301)

    def test_file_view_with_invalid_id(self):
        # Make a GET request to the view with a negative file ID
        # url = reverse('file', kwargs={'file_id': -1})  # Replace 'file' with the actual URL pattern name
        response = self.client.get("/compiler/file/" + str(-1))

        # Assert that the response is a JSON response
        # self.assertIsInstance(response, HTTPRespons)
        self.assertEqual(response.status_code, 404)


