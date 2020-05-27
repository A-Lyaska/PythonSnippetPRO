import os

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from main.models import Snippet


class TestIndexPage(TestCase):
    fixtures = ['test_db.json']

    def setUp(self):
        self.c = Client()
        user = User.objects.get(username='vasya')
        self.c.force_login(user)
        self.response = self.c.get(reverse('index'))

    def test_simple(self):
        self.assertEqual(self.response.context['pagename'], 'PythonBin v2.0')
        self.assertEqual(self.response.context['user'].username, 'vasya')
        self.assertTemplateUsed(self.response, 'pages/index.html')


class TestAddSnippetPage(TestCase):
    fixtures = ['test_db.json']

    def setUp(self):
        self.c = Client()
        user = User.objects.get(username='vasya')
        self.c.force_login(user)
        self.response = self.c.get(reverse('add_snippet'))

    def test_simple_get(self):
        self.assertEqual(self.response.context['pagename'], 'Добавление нового сниппета')
        self.assertTemplateUsed(self.response, 'pages/add_snippet.html')

    def test_simple_post(self):
        response = self.c.post(reverse('add_snippet'), {
            'name': '123', 'code': 'import this'
        })
        record = Snippet.objects.filter(name='123')
        self.assertEqual(len(record), 1)


class TestPep8SnippetPage(TestCase):
    fixtures = ['test_db.json']

    def setUp(self):
        self.c = Client()
        user = User.objects.get(username='vasya')
        self.c.force_login(user)
        self.c.post(reverse('add_snippet'), {'name': '123', 'code': '   a    =   b   +   c   '})
        self.record = Snippet.objects.filter(name='123').last()

    def test_get(self):
        response = self.c.get(reverse('view_format', kwargs={'snippet_id': self.record.id, 'utility': 'pep8'}))
        self.c.post(reverse('add_snippet'), {'name': '123', 'code': '   a    =   b   +   c   '})
        self.record = Snippet.objects.filter(name='123').last()
        self.assertEqual(response.context['code'], 'a = b + c\n')
        self.assertTrue(os.path.exists(self.record.get_filename('autopep8')))

    def test_invalid_get(self):
        response = self.c.get(reverse('view_format', kwargs={'snippet_id': 100, 'utility': 'pep8'}))
        self.assertEqual(response.status_code, 404)

