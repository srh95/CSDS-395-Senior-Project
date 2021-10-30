import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    User
)
from .forms import(
    RegisterForm,
    LoginForm
)

def index(request):
    return HttpResponse("Hello world. You're at the website index.")

def home(request):
    return render(request,'project/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                if(User.objects.get(user_username=form.cleaned_data['username'])):
                    messages.error(request, 'username already exists')
                    return HttpResponseRedirect('/accounts/register')
            except ObjectDoesNotExist:
                print('no users yet')

        if (form.cleaned_data['password1'] != form.cleaned_data['password2']):
            messages.error(request, 'Passwords do not match')
            return HttpResponseRedirect('/accounts/register/')
        database = User.objects.create(
            user_name=form.cleaned_data['name'],
            user_username=form.cleaned_data['username'],
            user_password=form.cleaned_data['password1']
        )
        database.save()
        return HttpResponseRedirect('/accounts/login/')
    else:
        form = RegisterForm()

    return render(request, 'project/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                if(User.objects.get(user_username=username) is None):
                    messages.error(request, 'Incorrect username')
                    return HttpResponseRedirect('/accounts/login/')
                if(User.objects.get(user_username=username)):
                    name = User.objects.get(user_username=username)
                    if(name.user_password != password):
                        messages.error(request, 'Incorrect password')
                        return HttpResponseRedirect('/accounts/login/')
                    url = 'home/' + str(name.id)
                    return HttpResponseRedirect(url)
            except ObjectDoesNotExist:
                    messages.error(request, 'Username does not exist')
                    return HttpResponseRedirect('/accounts/login/')
    else:
        form = LoginForm()

    return render(request, 'project/login.html', {'form': form})

def user_home(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id}
    return render(request, 'project/userHome.html', context)

def news(request):
    return render(request,'project/News.html')

def createBracket(request):
    return render(request, 'project/bracket.html')

# method to scrape for team names
def scoreScrape():
    url = "https://www.ncaa.com/march-madness-live/scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # scrape for first round teams
    content = soup.find('div', {'id': 'round-2'})
    teams1 = []
    for i in content.findAll('img'):
        teams1.append(i['alt'])

    # scrape for second round teams
    content = soup.find('div', {'id': 'round-3'})
    teams2 = []
    for i in content.findAll('img'):
        teams2.append(i['alt'])

    # scrape for sweet 16 teams
    content = soup.find('div', {'id': 'round-4'})
    teams16 = []
    for i in content.findAll('img'):
        teams16.append(i['alt'])

    # scrape for elite 8 teams
    content = soup.find('div', {'id': 'round-5'})
    teams8 = []
    for i in content.findAll('img'):
        teams8.append(i['alt'])

    # scrape for final 4 teams
    content = soup.find('div', {'id': 'round-6'})
    teams4 = []
    for i in content.findAll('img'):
        teams4.append(i['alt'])

    # scrape for final 4 teams
    content = soup.find('div', {'id': 'round-7'})
    teamsc = []
    for i in content.findAll('img'):
        teamsc.append(i['alt'])

    return teams1, teams2, teams16, teams8, teams4, teamsc

def scores(request):
    [teams1, teams2, teams16, teams8, teams4, teamsc] = scoreScrape()
    context = {'teams1': teams1, 'teams2': teams2, 'teams16': teams16, 'teams8': teams8, 'teams4': teams4, 'teamsc': teamsc}
    return render(request, 'project/scores.html', context)


def userScores(request, user_id):
    [teams1, teams2, teams16, teams8, teams4, teamsc] = scoreScrape()
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id, 'teams1': teams1, 'teams2': teams2, 'teams16': teams16, 'teams8': teams8, 'teams4': teams4, 'teamsc': teamsc}
    return render(request, 'project/userScores.html', context)

def teams(request):
    return render(request, 'project/teams.html')

