import requests
from bs4 import BeautifulSoup
import shutil
import os.path
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM



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
        dest = "/Users/sophiahall/Documents/CSDS-395-Senior-Project/method/project/static/team_img"
        # add img to directory if it doesn't already exist
        # don't download website logo
        if img == "/march-madness-live/public/assets/images/menu/mml-nav-logo.svg":
            continue
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
        # i need to replace the space with a dash and i need to remove all periods and then add .svg to the end
    #print("Losing teams")



    # scrape for winning teams and their scores
    content = soup.findAll('div', {'class': "active-team"})
    teamW = []
    for i in content:
        header = i.find('header')
        teamW.append(header.getText())
    #print("Winning teams")
    #print(teamW)

    return teamL, teamW, imgsL

def scores(request):
    [teamL, teamW, imgsL] = scoreScrape()
    context = {'teamL': teamL, 'teamW': teamW, 'img_name': imgsL}
    return render(request, 'project/scores.html', context)


def userScores(request, user_id):
    [teamL, teamW] = scoreScrape()
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id, 'teamL': teamL, 'teamW': teamW}
    return render(request, 'project/userScores.html', context)

def teams(request):
    return render(request, 'project/teams.html')

