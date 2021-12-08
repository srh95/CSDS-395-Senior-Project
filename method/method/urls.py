
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path
from project import views
from django.contrib import admin

app_name = 'project'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/home/<int:user_id>', views.user_home, name='userhome'),
    path('news/', views.news, name='news'),
    path('news/<int:user_id>', views.userNews, name='usernews'),
    path('myBracket/<int:user_id>', views.myBracket, name='bracket'),
    path('createBracket/<int:user_id>', views.createBracket, name='createBracket'),
    path('editBracket/<int:user_id>/<int:bracket_id>', views.editBracket, name='edit'),
    path('scores/', views.scores, name='scores'),
    path('scores/<int:user_id>', views.userScores, name='userscores'),
    path('teams/<int:user_id>', views.teams, name='teams'),
    path('createTeam/<int:user_id>', views.createTeam, name='createTeam'),
    path('joinTeam/<int:user_id>', views.joinTeam, name='joinTeam'),
    path('userTeams/<int:user_id>', views.userTeams, name='userteams'),
    path('leaveTeam/<int:user_id>', views.leaveTeam, name='leaveTeam'),
    path('prediction/<int:user_id>', views.prediction, name='prediction'),
]
