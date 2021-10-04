from django.shortcuts import render

from .models import (
    User

)

def index(request):
    return HttpResponse("Hello world. You're at the website index.")

def home(request):
    return render(request,'project/home.html')

def register(request):
    return render(request, 'project/register.html')

def login(request):
    return render(request, 'project/login.html')










