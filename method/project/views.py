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
import json
import string
from django.views.generic.list import ListView

from .models import (
    User, Bracket, Team
)

from .forms import (
    RegisterForm,
    LoginForm,
    StatForm,
    SaveForm,
    TeamForm,
    JoinTeamForm
)


def index(request):
    return HttpResponse("Hello world. You're at the website index.")


def home(request):
    return render(request, 'project/home.html')


def createTeam(request, user_id):
    # need to make it so a user cant create a team if team attribute is not null/empty
    # some way to check that the team ids are unique
    # display the team name and team member names on the teams page is a user belongs to a team \
    # if not just have create team or join team buttons
    user = get_object_or_404(User, pk=user_id)
    form = TeamForm(request.POST)
    brackets = Bracket.objects.filter(user__pk=user_id)
    context = {'user': user, 'brackets': brackets}
    if request.method == 'GET' and 'team_name' in request.GET:
        formteam_name = request.GET.get('team_name')
        if (Team.objects.get(team_name=formteam_name)):
            messages.error(request, 'Team name is taken')
            url = '/createTeam/' + str(user_id)
            return HttpResponseRedirect(url)
        s = 10  # number of characters in the string.
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=s))
        team_id = str(ran)
        database = Team.objects.create(
            team_id=team_id,
            team_name=request.GET.get('team_name'),
            num_members=request.GET.get('num_members')
        )
        database.save(),
        print(team_id)
        team_obj = get_object_or_404(Team, team_id=team_id)
        User.objects.filter(id=user_id).update(team=team_obj)
        favbracket = request.GET.get('enteredbracket')
        favbracket_obj = get_object_or_404(Bracket, bracket_name=favbracket)
        favbracketname = favbracket_obj.bracket_name
        User.objects.filter(id=user_id).update(favbracket=favbracketname)
        url = '/teams/' + str(user_id)
        return HttpResponseRedirect(url)

    else:
        context = {'user': user, 'user_id': user_id,'brackets': brackets, 'form': form}
        return render(request, 'project/createTeam.html', context)


def joinTeam(request, user_id):
    # need to check to see if team is at capacity, if it is dont allow them to join
    user = get_object_or_404(User, pk=user_id)
    form = JoinTeamForm(request.POST)
    brackets = Bracket.objects.filter(user__pk=user_id)
    context = {'user': user, 'brackets': brackets}
    if request.method == 'GET' and 'join_code' in request.GET:
        code = request.GET.get('join_code')
        team_obj = get_object_or_404(Team, team_id=code)
        teammates = User.objects.filter(team=team_obj)
        if (len(teammates) == team_obj.num_members):
            messages.error(request, 'Team is Full')
            url = '/joinTeam/' + str(user_id)
            return HttpResponseRedirect(url)
        favbracket = request.GET.get('enteredbracket')
        favbracket_obj = get_object_or_404(Bracket, bracket_name=favbracket)
        favbracketname = favbracket_obj.bracket_name
        User.objects.filter(id=user_id).update(team=team_obj)
        User.objects.filter(id=user_id).update(favbracket=favbracketname)
        url = '/teams/' + str(user_id)
        print('success')
        return HttpResponseRedirect(url)
    else:
        form = JoinTeamForm()
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'form': form}
        return render(request, 'project/joinTeam.html', context)


def leaveTeam(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # team = get_object_or_404(Team, team_id=user.team.team_id)
    if request.method == 'GET':
        User.objects.filter(id=user_id).update(team=None)
        url = '/teams/' + str(user_id)
        print('success')
        return HttpResponseRedirect(url)
    else:
        context = {'user': user, 'user_id': user_id}
        return render(request, 'project/joinTeam.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                if (User.objects.get(user_username=form.cleaned_data['username'])):
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
                if (User.objects.get(user_username=username) is None):
                    messages.error(request, 'Incorrect username')
                    return HttpResponseRedirect('/accounts/login/')
                if (User.objects.get(user_username=username)):
                    name = User.objects.get(user_username=username)
                    if (name.user_password != password):
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
    return render(request, 'project/News.html')


def userNews(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id}
    return render(request, 'project/userNews.html', context)


def userTeams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    favbracketname = user.favbracket
    brackets = Bracket.objects.filter(bracket_name=favbracketname)
    print(brackets)
    if user.team:
        team_obj = get_object_or_404(Team, team_id=user.team.team_id)
        teammates = User.objects.filter(team=team_obj)
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'teammates': teammates}
        return render(request, 'project/userTeams.html', context)
    else:
        context = {'user': user, 'user_id': user_id}
        return render(request, 'project/userTeams.html', context)


def createBracket(request, user_id):
    # only generate the bracket if the stats are put in
    # if a bracket is generated make the save button show up
    # delete the request sessions when a bracket is saved
    user = get_object_or_404(User, pk=user_id)
    # choosing the stats
    if request.method == 'GET' and 'stat1' in request.GET:
        stat1 = request.GET.get('stat1')
        request.session['stat1'] = stat1
        # establish some check to make sure no stat was chosen more than once
        # call function that generates bracket, returns list of teams in order to fill in bracket
        bracket = ["Virginia-Tech", "Colgate", "Arkansas", "Florida", "Drexel", "Illinois", "Utah St", "Texas Tech"]
        request.session['bracket'] = bracket
        context = {'user': user, 'user_id': user_id, 'bracket': bracket}
    else:
        context = {'user': user, 'user_id': user_id}

    # naming and saving the bracket
    if request.method == 'POST' and 'name' in request.POST:
        save_form = SaveForm(request.POST)
        if save_form.is_valid():
            bracket = request.session.get('bracket')
            # note to myself- it allows you to save a bracket without selecting stats, not good :(
            stat1 = request.session.get('stat1')
            database = Bracket.objects.create(
                bracket_name=save_form.cleaned_data['name'],
                user=user,
                bracket=bracket,
                stat1=stat1
            )
            database.save()
            del request.session['stat1']
            del request.session['bracket']
            context = {'user': user, 'user_id': user_id, 'bracket': bracket, 'save_form': save_form}

    else:
        save_form = SaveForm()
        context = {'user': user, 'user_id': user_id, 'save_form': save_form}

    return render(request, 'project/createBracket.html', context)


def myBracket(request, user_id):
    # scoring- split the list of winning teams into lists for each round
    # bracket is a list of teams- every 2 teams played a game against each other
    # split the bracket list up into lists for each round as well
    # for every team in bracket list we check if the name is in the winning teams list
    # if it is, then that team's name can be bolded on the bracket
    # idk how bracket scoring works so tbd if we can do that
    user = get_object_or_404(User, pk=user_id)
    print(user.user_username)
    brackets = Bracket.objects.filter(user__pk=user_id)

    for bracket in brackets:
        print(bracket.id)

    if request.method == 'GET' and 'bracket_id' in request.GET:
        bid = request.GET.get('bracket_id')
        Bracket.objects.filter(id=bid).delete()
        brackets = Bracket.objects.filter(user__pk=user_id)

    teamW = request.session.get('teamW')
    # separate list of winning teams into lists for each round
    round_1 = teamW[8:72]
    round_2 = teamW[72:104]
    sweet_16 = teamW[104:120]
    elite_8 = teamW[120:128]
    final_4 = teamW[128:132]
    championship = teamW[132:134]
    context = {'user': user, 'user_id': user_id, 'brackets': brackets}
    return render(request, 'project/bracket.html', context)


def deleteBracket(request, bracket_id):
    if request.method == 'GET':
        Bracket.objects.filter(id=bracket_id).delete()


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
        if os.path.isfile(dest + '/' + filename) == False:
            r = requests.get(img, stream=True)
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
        # img_info = header.getText()
        teamL.append(info)
        # imgname = info.replace(" ", "-")
        # img_name = ""
        # for char in imgname:
        #     if char not in ".'":
        #         img_name = img_name + char
        # imgsL.append("{% static 'team_img/" + img_name + ".svg"+"' %}")
        # imgsL.append(img_name)

    # scrape for winning teams and their scores
    content = soup.findAll('div', {'class': "active-team"})
    teamW = []
    for i in content:
        header = i.find('header')
        teamW.append(header.getText())

    return teamL, teamW, imgsL


def scores(request):
    [teamL, teamW, imgsL] = scoreScrape()
    context = {'teamL': teamL, 'teamW': teamW, 'img_name': json.dumps(imgsL)}
    return render(request, 'project/scores.html', context)


def userScores(request, user_id):
    [teamL, teamW, imgsL] = scoreScrape()
    request.session['teamW'] = teamW
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id, 'teamL': teamL, 'teamW': teamW, 'img_name': imgsL}
    return render(request, 'project/userScores.html', context)


def teams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id}
    return render(request, 'project/teams.html', context)
