"""
Модели Django размещаются здесь
"""

import hashlib
import os

from django.contrib.auth.models import User
from django.db import models

from main.formatter import AVAILABLE_FORMATTERS
from prom_sem_kr.settings import MEDIA_ROOT


class Snippet(models.Model):
    """
    Основная модель для хранения сниппетов

    :param name: название сниппета
    :param code: хранимый код (длинное текстовое поле)
    :param creation_date: дата создания, хранится в формате объекта ``datetime.datetime()``
    :param user: ForeignKey к модели :class:`django.contrib.auth.models.User`
    :param sha1: SHA1-хеш хранимого кода. Используется для имени файла
    :param sha256: SHA256-хеш хранимого кода
    :param md5: MD5-хеш хранимого кода
    :param code: временное хранилище кода перед записью в файл.
                 Устанавливается **после запуска** конструктора вручную
    """
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             blank=True, null=True)  # can be empty due to usage of AnonymousUser
    sha1 = models.TextField(max_length=40)
    sha256 = models.TextField(max_length=64)
    md5 = models.TextField(max_length=32)
    code = ''

    def get_sha1(self):
        """
        Получение SHA1-хеша

        Используется библиотека hashlib

        :return: хеш в виде строки
        """
        hell = hashlib.sha1(self.code.encode('utf8'))
        return hell.hexdigest()

    def get_sha256(self):
        """
        Получение SHA256-хеша

        Используется библиотека hashlib

        :return: хеш в виде строки
        """
        hell = hashlib.sha256(self.code.encode('utf8'))
        return hell.hexdigest()

    def get_md5(self):
        """
        Получение MD5-хеша

        Используется библиотека hashlib

        :return: хеш в виде строки
        """
        hell = hashlib.md5(self.code.encode('utf8'))
        return hell.hexdigest()

    def get_filename(self, modifier=None):
        """
        Получение имени файла

        Используется для получения имён оргинального файла и файлов с отформатированным кодом

        * Формат 1: sha1hash.py
        * Формат 2 (если указана утилита): sha1hash_utility.py

        :param modifier: имя утилиты
        :type modifier: :class:`str`
        :return: Имя файла
        """
        path = os.path.join(MEDIA_ROOT, '{}'.format(self.sha1))
        if modifier:
            path += '_' + modifier
        path += '.py'
        return path

    def save_to_file(self, modifier=None, code=None):
        """
        Сохранение указанного кода в указанный файл.

        Если код не указан - используется оригинальный код сниппета
        Если модификатор не указан - используется оригинальный файл сниппета

        :param modifier: имя утилиты
        :type modifier: :class:`str`
        :param code: код сниппета (возможно, отформатированный)
        :type code: :class:`str`
        """
        path = self.get_filename(modifier)
        if not code:
            code = self.code
        with open(path, 'w') as file:
            file.write(code.replace('\r\n', '\n'))

    def get_code(self):
        """
        Загрузка оригинального кода сниппета из файла.

        :return: Код в виде строки
        """
        if not os.path.exists(self.get_filename()):
            raise self.DoesNotExist
        with open(self.get_filename(), 'r') as file:
            data = file.read()
        return data

    def get_formatted_code(self, utility):
        """
        Получение кода, отформатированного одной из подддерживаемых утилит

        :raises: :class:`Snippet.DoesNotExist` в случае, указаная утилита не поддерживается
        :return: Форматированный код в виде строки
        """
        if utility not in AVAILABLE_FORMATTERS:
            raise self.DoesNotExist
        return AVAILABLE_FORMATTERS[utility](self.get_filename()).get_formatted_code()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Сохранение записи о сниппете в БД

        В момент вызова вычисляются и сохраняются хеши. Также оригинальный код сохраняется в файл.
        """
        self.md5 = self.get_md5()
        self.sha1 = self.get_sha1()
        self.sha256 = self.get_sha256()
        self.save_to_file()
        super().save()
