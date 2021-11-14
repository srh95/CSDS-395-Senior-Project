import requests
import random
from bs4 import BeautifulSoup
import shutil
import os.path
import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    User, Bracket, Group, Pin
)
from .forms import(
    RegisterForm,
    LoginForm,
    StatForm,
    SaveForm,
)

def index(request):
    return HttpResponse("Hello world. You're at the website index.")

def home(request):
    return render(request,'project/home.html')

def createteam(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            x = random.randomint(1000,2000)
            print(x)
        database = Team.objects.create(
            user_name=form.cleaned_data['name'],
            user_username=form.cleaned_data['username'],
            user_password=form.cleaned_data['password1']
        )
        database.save()
    else:
        print("Team cannot be created")



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

def createteam(request):
    return render(request,'project/createTeam.html')

def jointeam(request):
    return render(request, 'project/jointeam.html')

def userteam(request):
    return render(request, 'project/userTeams.html')

def news(request):
    return render(request,'project/News.html')

def userNews(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id}
    return render(request, 'project/userNews.html', context)

def createBracket(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # initialize the stats
    stat1 = []
    stat2 = []
    stat3 = []
    stat4 = []
    stat5 = []
    # initializing the bracket
    bracket = []

    # choosing the stats
    if request.method == 'POST' and 'stat1' in request.POST:
        create_form = StatForm(request.POST)
        if create_form.is_valid():
            print("Form is valid")
            stat1 = create_form.cleaned_data['stat1']
            stat2 = create_form.cleaned_data['stat2']
            stat3 = create_form.cleaned_data['stat3']
            stat4 = create_form.cleaned_data['stat4']
            stat5 = create_form.cleaned_data['stat5']

            ordered_stats = [stat1, stat2, stat3, stat4, stat5]
            print(stat5)
            # establish some check to make sure no stat was chosen more than once
            # call function that generates bracket, returns list of teams in order to fill in bracket
            bracket = ["Virginia-Tech", "Colgate", "Arkansas", "Florida", "Drexel", "Illinois", "Utah St", "Texas Tech"]
            context = {'user': user, 'user_id': user_id, 'form': create_form, 'bracket': bracket}
    else:
        create_form = StatForm()
        context = {'user': user, 'user_id': user_id, 'form': create_form, 'bracket': bracket}

    # naming and saving the bracket
    if request.method == 'POST' and 'name' in request.POST:
            save_form = SaveForm(request.POST)
            print("saved the form")
            if save_form.is_valid():
                print("Form is valid")
                print(save_form.cleaned_data['name'])
                print(stat5)
                print(user_id)
                database = Bracket.objects.create(
                    bracket_name=save_form.cleaned_data['name'],
                    user=user,
                    bracket=bracket,
                    stat1=stat1,
                    stat2=stat2,
                    stat3=stat3,
                    stat4=stat4,
                    stat5=stat5,
                )
                database.save()
                context = {'user': user, 'user_id': user_id, 'form': create_form, 'bracket': bracket, 'save_form': save_form}

    else:
        save_form = SaveForm()
        context = {'user': user, 'user_id': user_id, 'form': create_form, 'bracket': bracket, 'save_form': save_form}


    return render(request, 'project/createBracket.html', context)

def myBracket(request,user_id):
    user = get_object_or_404(User, pk=user_id)
    brackets = Bracket.objects.filter(user__pk=user_id)
    context = {'user': user, 'user_id': user_id, 'brackets': brackets}
    return render(request, 'project/bracket.html', context)

# method to scrape for game info
def scoreScrape():
    url = "https://www.ncaa.com/march-madness-live/scores"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # scrape for team images
    content = soup.findAll('img')
    imgs = []
    for i in content:
        imgs.append(i.attrs['src'])

    for img in imgs:
        filename = img.split("/")[-1]
        current_path = os.path.abspath(__file__)
        size = len(current_path)
        dest = current_path[:size - 8]
        dest = dest + 'static/team_img'
        # don't download website logo
        if img == "/march-madness-live/public/assets/images/menu/mml-nav-logo.svg":
            continue
        # add img to directory if it doesn't already exist
        if os.path.isfile(dest +'/' + filename) == False:
            r = requests.get(img, stream = True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                    shutil.move(filename, dest)
                print('Image sucessfully Downloaded: ', filename)
            else:
                print('Image Couldn\'t be retreived')

    # scrape for losing teams and their scores
    content = soup.findAll('div', {'class': "inactive-team"})
    teamL = []
    imgsL = []
    for i in content:
        header = i.find('header')
        info = header.getText()
        img_info = header.getText()
        teamL.append(info)
        imgname = info.replace(" ", "-")
        img_name = ""
        for char in imgname:
            if char not in ".'":
                img_name = img_name + char
        imgsL.append("{% static 'team_img/" + img_name + ".svg"+"' %}")

    # scrape for winning teams and their scores
    content = soup.findAll('div', {'class': "active-team"})
    teamW = []
    for i in content:
        header = i.find('header')
        teamW.append(header.getText())

    return teamL, teamW, imgsL

def scores(request):
    [teamL, teamW, imgsL] = scoreScrape()
    context = {'teamL': teamL, 'teamW': teamW, 'img_name': imgsL}
    return render(request, 'project/scores.html', context)


def userScores(request, user_id):
    [teamL, teamW, imgsL] = scoreScrape()
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id, 'teamL': teamL, 'teamW': teamW, 'img_name': imgsL}
    return render(request, 'project/userScores.html', context)

def teams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id}
    return render(request, 'project/teams.html', context)

