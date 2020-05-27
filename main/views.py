"""
View-функции Django размещаются здесь
"""

import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer

from main.forms import LoginForm, BaseSnippetForm
from main.models import Snippet


def get_base_context(request, pagename):
    """
    Получение базового контекста

    :param request: объект c деталями запроса.
    Используется для получения авторизованного пользователя
    :type request: :class:`django.http.HttpRequest`
    :return: словарь с предустановленными значениями
    :rtype: :class:`dict`
    """
    return {
        'pagename': pagename,
        'loginform': LoginForm(),
        'user': request.user,
    }


def index_page(request):
    """
    Заглавная страница

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри
    :rtype: :class:`django.http.HttpResponse`
    """
    context = get_base_context(request, 'PythonBin v2.0')
    return render(request, 'pages/index.html', context)


@login_required(login_url='/login/')
def add_snippet_page(request):
    """
    Страница добавления сниппета

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри в случае,
    если идёт GET-запрос на страницу
    :return: перенаправление на главную страницу в случае POST-запроса
    :raises: :class:`django.http.Http404` в случае,
    если сниппет с указанным ID не существует
    """
    context = get_base_context(request, 'Добавление нового сниппета')
    if request.method == 'POST':
        addform = BaseSnippetForm(request.POST)
        if addform.is_valid():
            record = Snippet(
                name=addform.data['name'],
                creation_date=datetime.datetime.now(tz=timezone.utc),
                user=request.user
            )
            record.code = addform.data['code']
            record.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Сниппет успешно добавлен")
            return redirect('view_snippet', snippet_id=record.id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме")
            return redirect('add_snippet')
    else:
        context['addform'] = BaseSnippetForm(
            initial={
                'user': request.user.username,
            }
        )
        return render(request, 'pages/add_snippet.html', context)


@login_required(login_url='/login/')
def view_snippet_page(request, snippet_id):
    """
    Отображение определённого сниппета

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :param snippet_id: primary key в модели :class:`main.views.Snippet`
    :type snippet_id: int
    :return: объект ответа сервера с HTML-кодом внутри
    :rtype: :class:`django.http.HttpResponse`
    :raises: :class:`django.http.Http404` в случае,
    если сниппет с указанным ID не существует
    """
    context = get_base_context(request, 'Просмотр сниппета')
    try:
        record = Snippet.objects.get(id=snippet_id, user=request.user)
        context['record'] = record
        context['addform'] = BaseSnippetForm(
            initial={
                'user': record.user.username,
                'name': record.name,
                'md5': record.md5,
                'sha256': record.sha256,
            }
        )
        context['pygmentcode'] = highlight(
            record.get_code(), PythonLexer(), HtmlFormatter())
        context['pygmentstyle'] = HtmlFormatter().get_style_defs('.highlight')
    except Snippet.DoesNotExist:
        raise Http404
    return render(request, 'pages/view_snippet.html', context)


def login_page(request):
    """
    Самописная функция авторизации

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: перенаправление на главную страницу
    """
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.data['username']
            password = loginform.data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS,
                                     "Авторизация успешна")
            else:
                messages.add_message(request, messages.ERROR,
                                     "Неправильный логин или пароль")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме авторизации")
    return redirect('index')


def logout_page(request):
    """
    Самописная функция деавторизации

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: перенаправление на главную страницу
    """
    logout(request)
    messages.add_message(request, messages.INFO,
                         "Вы успешно вышли из аккаунта")
    return redirect('index')


@login_required(login_url='/login/')
def my_snippets_page(request):
    """
    Отображение списка всех сниппетов, когда-либо созданных пользователем

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри
    """
    context = get_base_context(request, 'Мои сниппеты')
    context['records'] = Snippet.objects.filter(user=request.user)
    context['count'] = len(context['records'])
    return render(request, 'pages/my_snippets.html', context)


def view_formatted_code_page(request, snippet_id, utility):
    """
    Получение кода, отформатированноего одной из поддерживаемых утилит

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :param snippet_id: id сниппета
    :type snippet_id: :class:`int`
    :param utility: имя утилиты
    :type utility: :class:`str`
    :raises: :class:`django.http.Http404` в случае,
    если сниппет с указанным ID не существует
    :raises: :class:`django.http.Http404` в случае,
    если указанная утилита не поддерживается
    :return: объект ответа сервера с HTML-кодом внутри
    """
    context = get_base_context(request, 'Форматирование {}'.format(utility))
    try:
        record = Snippet.objects.get(id=snippet_id, user=request.user)
        context['record'] = record
        context['addform'] = BaseSnippetForm(
            initial={
                'user': record.user.username,
                'name': record.name,
            }
        )
        formatted_code = record.get_formatted_code(utility)
        context['code'] = formatted_code
        context['pygmentcode'] = highlight(formatted_code,
                                           PythonLexer(), HtmlFormatter())
        context['pygmentstyle'] = HtmlFormatter().get_style_defs('.highlight')
    except Snippet.DoesNotExist:
        raise Http404
    return render(request, 'pages/base_snippet.html', context)


@login_required(login_url='/login/')
def delete_snippet_page(request, snippet_id):
    """
    Удаление сниппета

    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :param snippet_id: id сниппета
    :type snippet_id: :class:`int`
    :raises: :class:`django.http.Http404` в случае,
    если сниппет с указанным ID не существует
    :raises: :class:`django.http.Http404` в случае,
    если сниппет с указанным ID не принадлежит пользователю
    :return: перенаправление на страницу списка сниппетов
    :return: перенаправление на страницу логина
    в случае неавторизованного пользователя
    """
    records = Snippet.objects.filter(id=snippet_id, user=request.user)
    if records.count() == 0:
        raise Http404
    context = get_base_context(request, 'Удаление сниппета')

    if request.POST:
        record = Snippet.objects.get(id=snippet_id)
        record.delete()
        return redirect('my_snippets')
    return render(request, 'pages/delete_snippet.html', context)
