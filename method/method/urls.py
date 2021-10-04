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

from django.urls import path, include
from project import views
from django.contrib import admin
app_name = 'project'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/register/',views.register, name='register'),
    path('accounts/login/user/home/<int:user_id>', views.user_home, name='home')
]
