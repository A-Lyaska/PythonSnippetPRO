"""
Классы для работы с утилитами автоформатирования кода
"""

import os
from shutil import copyfile
import autopep8

class BaseFormatter:
    """
    Основная модель для хранения сниппетов

    Идея работы проста: сначала создаётся объект форматтера, потом вызывается метод `get_formatted_code`.
    Он проверяет существование файла с отформатированным кодом.
    Если файл есть - данные берутся из него, если его нет - запускается утилита и данные записываются в файл.

    :param UTILITY: название утилиты (python-модуля или консольной утилиты)
    """
    UTILITY = None

    def __init__(self, filename):
        """
        Конструктор объекта.

        Сохраняет имя оригинального файла.

        :param filename: имя оригинального файла
        """
        self.filename = filename

    def get_formatted_code_name(self):
        """
        Получение имя файла с кодом.

        В случае, если утилита не указана, используется имя оригинального файла,
        иначе - в конец имени подставляется утилита.

        :param filename: имя оригинального файла
        :return: имя файла
        :rtype: :class:`str`
        """
        if self.UTILITY:
            return '{}_{}.py'.format(self.filename[:-3], self.UTILITY)
        else:
            return self.filename

    def formatted_code_exists(self):
        """
        Проверка существования файла с кодом

        :return: логическое значение
        :rtype: :class:`bool`
        """
        return os.path.exists(self.get_formatted_code_name())

    @staticmethod
    def get_code_from_file(filename):
        """
        Получение данных из файла по имеющемуся имени

        :param filename: имя файла
        :return: код, хранящийся в файле.
        :rtype: :class:`str`
        """
        with open(filename, 'r') as f:
            code=f.read()
        return code

    def save_formatted_code_to_file(self):
        """
        Сохранение отформатированного утилитой кода в файл. Заготовка для наследных классов

        :raises: :class:`NotImplementedError` ибо это всего лишь прототип.
        """
        raise NotImplementedError


    def get_formatted_code(self):
        """
        Получение форматированного кода на основе имеющегося имени файла с оригинальным кодом.

        :return: форматированный код.
        :rtype: :class:`str`
        """
        if not self.formatted_code_exists():
            self.save_formatted_code_to_file()
        return self.get_code_from_file(self.get_formatted_code_name())


class Pep8Formatter(BaseFormatter):
    """
    Класс, форматирующий код через autopep8

    autopep8 - утилита, форматирующая код в соответствии с рекомендациями PEP8
    """
    UTILITY = 'autopep8'

    def save_formatted_code_to_file(self):
        """
        Сохранение отформатированного через autopep8 кода в файл

        Утилита вызывается через программный интерфейс
        """
        with open(self.filename, 'r') as f:
            self.code = f.read()
        fixed_code = autopep8.fix_code(self.code, options={'aggressive': 1})
        with open(self.get_formatted_code_name(), 'w') as f:
            f.write(fixed_code)


class CommandLineFormatter(BaseFormatter):
    """
    Базовый класс для всех утилит, работающих из командной строки.

    :param OPTS: параметры запуска утилиты (все, кроме имени обрабатываемого файла)
    """
    OPTS = ''


    def __init__(self, filename):
        """
        Конструктор объекта.

        В ходе работы пытается импортировать утилиту в виде python-модуля
        :raises: :class:`ModuleNotFoundError` в случае, если утилита не установлена.
        """
        super().__init__(filename)
        __import__(self.UTILITY)

    def save_formatted_code_to_file(self):
        """
        Сохранение кода, отформатированного через консольную утилиту, в файл

        Формат работы: исходный код сначала копируется в результирующий файл,
        затем над ним производятся требуемые действия
        """
        copyfile(self.filename, self.get_formatted_code_name())
        os.system('{} {} {}'.format(
            self.UTILITY,
            self.OPTS,
            self.get_formatted_code_name()
        ))


class DocFormatter(CommandLineFormatter):
    """
    Класс, форматирующий код через docformatter

    docformatter - утилита, приводящая doc-строки в соответствие с рекомендациям PEP257
    """
    UTILITY = 'docformatter'
    OPTS = '--pre-summary-newline --in-place'


class AutoFlakeFormatter(CommandLineFormatter):
    """
    Класс, форматирующий код через autoflake

    autoflake - утилита, чистящая код от неиспользуемых импортов и переменных
    """
    UTILITY = 'autoflake'
    OPTS = '--remove-all-unused-imports ' \
           '--remove-duplicate-keys ' \
           '--remove-unused-variables ' \
           '--in-place'


AVAILABLE_FORMATTERS = {
    'pep8': Pep8Formatter,
    'docformatter': DocFormatter,
    'autoflake': AutoFlakeFormatter,
}
