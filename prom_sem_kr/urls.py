"""prom_sem_kr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),
    path('snippets/add', views.add_snippet_page, name='add_snippet'),
    path('snippets/list', views.my_snippets_page, name='my_snippets'),
    path('snippets/<int:snippet_id>', views.view_snippet_page, name='view_snippet'),
    path('snippets/<int:snippet_id>/format/<str:utility>', views.view_formatted_code_page, name='view_format'),
    path('snippets/<int:snippet_id>/delete', views.delete_snippet_page, name='delete_snippet'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
]
