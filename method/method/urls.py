"""method URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path
from project import views
from django.contrib import admin
app_name = 'project'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/register/',views.register, name='register'),
    path('accounts/login/home/<int:user_id>', views.user_home, name='userhome'),
    path('news/', views.news, name='news'),
    path('myBracket/<int:user_id>', views.myBracket, name='bracket'),
    path('createBracket/<int:user_id>', views.createBracket, name='createBracket'),
    path('scores/', views.scores, name='scores'),
    path('scores/<int:user_id>', views.userScores, name='userscores'),
    path('teams/', views.teams, name='teams'),

]
