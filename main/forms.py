from django import forms


class LoginForm(forms.Form):
    """
    Форма авторизации. Используется в :func:`main.views.login_page`

    :param username: имя пользователя
    :param password: пароль пользователя
    """
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Username', })
    )
    password = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Password', })
    )


class BaseSnippetForm(forms.Form):
    """
    Форма работы со сниппетом.
    Используется во view-функциях для добавления и/или просмотра

    :param name: имя сниппета
    :param user: пользователь.
    Подставляется автоматически на основе данных об авторизации
    :param code: сам сниппет
    :param md5: md5-хеш сниппета
    :param sha256: SHA256-хеш сниппета
    """
    name = forms.CharField(
        label='Название',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    user = forms.CharField(
        label='Пользователь',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'disabled': '', }),
        required=False
    )
    md5 = forms.CharField(
        label='MD5',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'disabled': '', }),
        required=False
    )
    sha256 = forms.CharField(
        label='SHA256',
        max_length=64,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'disabled': '', }),
        required=False
    )
    code = forms.CharField(
        label='Код',
        max_length=5000,
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'style': 'height:500px'})
    )
