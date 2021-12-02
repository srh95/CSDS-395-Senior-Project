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
import re
import pandas as pd
from urllib.request import urlopen, Request
import datetime
from django.views.generic.list import ListView

from .models import (
    User, Bracket, Team, Posts
)

from .forms import (
    RegisterForm,
    LoginForm,
    SaveForm,
    TeamForm,
    JoinTeamForm,
    PostForm
)


def index(request):
    return HttpResponse("Hello world. You're at the website index.")

def isTournamentStarted():
    # lock brackets on the day march madness begins
    # get today's date
    today = datetime.datetime.now()
    # tournament start date
    tournament = "15/3/2022 0:00"
    tournament = datetime.datetime.strptime(tournament, "%d/%m/%Y %H:%M")

    if today > tournament:
        open = False
    else:
        open = True

    return open

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
        if form.is_valid():
            try:
                if (Team.objects.get(team_name=formteam_name)):
                    messages.error(request, 'Team name is taken')
                    url = '/createTeam/' + str(user_id)
                    return HttpResponseRedirect(url)
            except ObjectDoesNotExist:
                print('no teams yet')
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
        User.objects.filter(id=user_id).update(favbracket=favbracket_obj)
        url = '/teams/' + str(user_id)
        return HttpResponseRedirect(url)

    else:
        context = {'user': user, 'user_id': user_id,'brackets': brackets, 'form': form}
        return render(request, 'project/createTeam.html', context)


def joinTeam(request, user_id):
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
        User.objects.filter(id=user_id).update(team=team_obj)
        User.objects.filter(id=user_id).update(favbracket=favbracket_obj)
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
    create = isTournamentStarted()
    context = {'user': user, 'user_id': user_id, 'create': create}
    return render(request, 'project/userHome.html', context)


def news(request):
    allposts = Posts.objects.all()
    context = {'allposts': allposts}
    return render(request, 'project/News.html', context)


def userNews(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    allposts = Posts.objects.all()
    form = PostForm(request.POST)
    context = {'user': user, 'user_id': user_id, 'allposts': allposts, 'form': form}
    if request.method == 'POST' and 'content' in request.POST:
        if form.is_valid():
            # note to myself- it allows you to save a bracket without selecting stats, not good :(
            database = Posts.objects.create(
                user=user,
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content']
            )
            database.save()
            context = {'user': user, 'user_id': user_id, 'form': form, 'allposts': allposts}
    else:
        form = PostForm()
        context = {'user': user, 'user_id': user_id, 'form': form, 'allposts': allposts}

    return render(request, 'project/userNews.html', context)

def userTeams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    favbracketname = user.favbracket
    brackets = Bracket.objects.filter(bracket_name=favbracketname)
    print(brackets)
    if user.team:
        team_obj = get_object_or_404(Team, team_id=user.team.team_id)
        teammates = User.objects.filter(team=team_obj)
        num_teammates = len(teammates)
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'teammates': teammates, 'num_teammates': num_teammates}
        return render(request, 'project/userTeams.html', context)
    else:
        context = {'user': user, 'user_id': user_id}
        return render(request, 'project/userTeams.html', context)

def generate2021Teams():
    bracket_64 = ['gonzaga', 'norfolk-state', 'oklahoma', 'missouri', 'creighton', 'california-santa-barbara',
                  'virginia', 'ohio', 'southern-california', 'drake', 'kansas', 'eastern-washington', 'oregon',
                  'virginia-commonwealth', 'iowa', 'grand-canyon', 'michigan', 'texas-southern', 'louisiana-state',
                  'st-bonaventure', 'colorado', 'georgetown', 'florida-state', 'north-carolina-greensboro',
                  'brigham-young', 'ucla', 'texas-southern', 'abilene-christian', 'connecticut', 'maryland',
                  'alabama', 'iona', 'baylor', 'hartford', 'north-carolina', 'wisconsin', 'villanova', 'winthrop',
                  'purdue', 'north-texas', 'texas-tech', 'utah-state', 'arkansas', 'colgate', 'florida',
                  'virginia-tech', 'ohio-state', 'oral-roberts', 'illinois', 'drexel', 'loyola-il', 'georgia-tech',
                  'tennessee', 'oregon-state', 'oklahoma-state', 'liberty', 'san-diego-state', 'syracuse',
                  'west-virginia', 'morehead-state', 'clemson', 'rutgers', 'houston', 'cleveland-state']
    it = iter(bracket_64)
    bracket_2021 = list(zip(it, it))
    return bracket_64, bracket_2021

def createBracket(request, user_id):
    # only generate the bracket if the stats are put in
    # if a bracket is generated make the save button show up
    # delete the request sessions when a bracket is saved
    # list of first round teams
    user = get_object_or_404(User, pk=user_id)
    bracket_64, bracket_2021 = generate2021Teams()
    # choosing the stats
    if request.method == 'GET' and 'stat1' in request.GET and 'stat2' in request.GET \
            and 'stat3' in request.GET and 'stat4' in request.GET and 'stat5' in request.GET:
        stat1 = request.GET.get('stat1')
        stat2 = request.GET.get('stat2')
        stat3 = request.GET.get('stat3')
        stat4 = request.GET.get('stat4')
        stat5 = request.GET.get('stat5')

        request.session['stat1'] = stat1
        request.session['stat2'] = stat2
        request.session['stat3'] = stat3
        request.session['stat4'] = stat4
        request.session['stat5'] = stat5

        ordered_stats = [stat1, stat2, stat3, stat4, stat5]
        # remove none's from the list
        valueToBeRemoved = "None"
        try:
            while True:
                ordered_stats.remove(valueToBeRemoved)
        except ValueError:
            pass

        # check that different stat was selected for each category
        if len(set(ordered_stats)) != len(ordered_stats):
            messages.error(request, 'Please select a distinct statistic for each category (or none) to generate a bracket')
            context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64}
            # append nones back 5-length to tell how many
        else:
            # pass ordered_stats into function
            '''
            round_32 = next_round_2021(bracket_2021, stat1, stat2, stat3, stat4, stat5)
            print("round of 32 was generated")
            sweet_16 = next_round_2021(round_32, stat1, stat2, stat3, stat4, stat5)
            print("round of 16 was generated")
            elite_8 = next_round_2021(sweet_16, stat1, stat2, stat3, stat4, stat5)
            final_4 = next_round_2021(elite_8, stat1, stat2, stat3, stat4, stat5)
            championship = next_round_2021(final_4, stat1, stat2, stat3, stat4, stat5)
            winner = compare_schools_2021(championship[0][0], championship[0][1], stat1, stat2, stat3, stat4, stat5)
            print(winner)
            '''
            bracket_32 = ['gonzaga', 'oklahoma', 'creighton', 'ohio', 'southern-california', 'eastern-washington', 'oregon',
                    'iowa', 'texas-southern', 'louisiana-state', 'georgetown', 'florida-state',
                    'brigham-young', 'abilene-christian', 'connecticut', 'alabama', 'baylor', 'north-carolina',
                    'winthrop', 'purdue', 'utah-state', 'colgate', 'florida', 'ohio-state', 'illinois', 'georgia-tech',
                    'tennessee', 'oklahoma-state', 'syracuse', 'west-virginia', 'rutgers', 'houston']
            bracket_16 = ['gonzaga', 'ohio', 'eastern-washington', 'iowa', 'texas-southern', 'georgetown', 'abilene-christian',
                          'alabama', 'north-carolina', 'winthrop', 'colgate', 'ohio-state' 'illinios',
                          'oklahoma-state', 'west-virginia', 'houston']
            bracket_8 = ['gonzaga', 'iowa', 'texas-southern', 'alabama', 'winthrop', 'colgate', 'illinios', 'houston']
            bracket_4 = ['iowa', 'alabama', 'colgate', 'illinois']
            bracket_2 = ['iowa', 'colgate']
            winner = ['colgate']
            # call function that generates bracket, returns list of teams in order to fill in bracket
            request.session['bracket_32'] = bracket_32
            request.session['bracket_16'] = bracket_16
            request.session['bracket_8'] = bracket_8
            request.session['bracket_4'] = bracket_4
            request.session['bracket_2'] = bracket_2
            request.session['winner'] = winner

            context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'bracket_32': bracket_32,
                       'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4, 'bracket_2': bracket_2,
                       'winner': winner}

    else:
        context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64}

    # naming and saving the bracket
    if request.method == 'POST' and 'name' in request.POST:
        save_form = SaveForm(request.POST)
        if save_form.is_valid():
            try:
                bracket_32 = request.session.get('bracket_32')
                bracket_16 = request.session.get('bracket_16')
                bracket_8 = request.session.get('bracket_8')
                bracket_4 = request.session.get('bracket_4')
                bracket_2 = request.session.get('bracket_2')
                winner = request.session.get('winner')
                # note to myself- it allows you to save a bracket without selecting stats, not good :(
                stat1 = request.session.get('stat1')
                stat2 = request.session.get('stat2')
                stat3 = request.session.get('stat3')
                stat4 = request.session.get('stat4')
                stat5 = request.session.get('stat5')

                stats = [stat1, stat2, stat3, stat4, stat5]
                database = Bracket.objects.create(
                    bracket_name=save_form.cleaned_data['name'],
                    user=user,
                    bracket_64=bracket_64,
                    bracket_32=bracket_32,
                    bracket_16=bracket_16,
                    bracket_8=bracket_8,
                    bracket_4=bracket_4,
                    bracket_2=bracket_2,
                    winner=winner,
                    stats=stats
                )
                database.save()
                del request.session['stat1']
                del request.session['stat2']
                del request.session['stat3']
                del request.session['stat4']
                del request.session['stat5']
                del request.session['bracket_32']
                del request.session['bracket_16']
                del request.session['bracket_8']
                del request.session['bracket_4']
                del request.session['bracket_2']
                del request.session['winner']
                context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'save_form': save_form}
            except:
                messages.error(request,
                               'You must select stats and generate a bracket before saving')


        else:
            save_form = SaveForm()
            context = {'user': user, 'user_id': user_id, 'save_form': save_form, 'bracket_64': bracket_64}

    return render(request, 'project/createBracket.html', context)


def myBracket(request, user_id):
    # scoring- split the list of winning teams into lists for each round
    # bracket is a list of teams- every 2 teams played a game against each other
    # split the bracket list up into lists for each round as well
    # for every team in bracket list we check if the name is in the winning teams list
    # if it is, then that team's name can be bolded on the bracket
    # idk how bracket scoring works so tbd if we can do that
    user = get_object_or_404(User, pk=user_id)
    brackets = Bracket.objects.filter(user__pk=user_id)

    # request to remove bracket
    if request.method == 'GET' and 'bracket_id' in request.GET:
        bid = request.GET.get('bracket_id')
        Bracket.objects.filter(id=bid).delete()
        brackets = Bracket.objects.filter(user__pk=user_id)
        for bracket in brackets:
            print(bracket.id)

    # request to edit bracket
    if request.method == 'GET' and 'bracketid' in request.GET:
        bid = request.GET.get('bracketid')
        editBracket(request, bid, user_id)

    edit = isTournamentStarted()

    # scoring stuff
    teamW = request.session.get('teamW')
    # separate list of winning teams into lists for each round
    # round_1 = teamW[8:72]
    # round_2 = teamW[72:104]
    # sweet_16 = teamW[104:120]
    # elite_8 = teamW[120:128]
    # final_4 = teamW[128:132]
    # championship = teamW[132:134]
    context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'edit': edit}
    return render(request, 'project/bracket.html', context)


def editBracket(request, bracket_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    brackets = Bracket.objects.filter(id=bracket_id)
    bracket=brackets[0]

    bracket_64, bracket_2021 = generate2021Teams()
    # choosing the stats
    if request.method == 'GET' and 'stat1' in request.GET and 'stat2' in request.GET \
            and 'stat3' in request.GET and 'stat4' in request.GET and 'stat5' in request.GET:
        stat1 = request.GET.get('stat1')
        stat2 = request.GET.get('stat2')
        stat3 = request.GET.get('stat3')
        stat4 = request.GET.get('stat4')
        stat5 = request.GET.get('stat5')

        request.session['stat1'] = stat1
        request.session['stat2'] = stat2
        request.session['stat3'] = stat3
        request.session['stat4'] = stat4
        request.session['stat5'] = stat5

        ordered_stats = [stat1, stat2, stat3, stat4, stat5]
        # remove none's from the list
        valueToBeRemoved = "None"

        try:
            while True:
                ordered_stats.remove(valueToBeRemoved)
        except ValueError:
            pass

        if len(set(ordered_stats)) != len(ordered_stats):
            messages.error(request, 'Please select a different statistic for each category')
            # append nones back 5-length to tell how many
        else:
            # pass ordered_stats into function
            '''
            round_32 = next_round_2021(bracket_2021, stat1, stat2, stat3, stat4, stat5)
            print("round of 32 was generated")
            sweet_16 = next_round_2021(round_32, stat1, stat2, stat3, stat4, stat5)
            print("round of 16 was generated")
            elite_8 = next_round_2021(sweet_16, stat1, stat2, stat3, stat4, stat5)
            final_4 = next_round_2021(elite_8, stat1, stat2, stat3, stat4, stat5)
            championship = next_round_2021(final_4, stat1, stat2, stat3, stat4, stat5)
            winner = compare_schools_2021(championship[0][0], championship[0][1], stat1, stat2, stat3, stat4, stat5)
            print(winner)
            '''
            bracket_32 = ['gonzaga', 'oklahoma', 'creighton', 'ohio', 'southern-california', 'eastern-washington',
                          'oregon',
                          'iowa', 'texas-southern', 'louisiana-state', 'georgetown', 'florida-state',
                          'brigham-young', 'abilene-christian', 'connecticut', 'alabama', 'baylor', 'north-carolina',
                          'winthrop', 'purdue', 'utah-state', 'colgate', 'florida', 'ohio-state', 'illinois',
                          'georgia-tech',
                          'tennessee', 'oklahoma-state', 'syracuse', 'west-virginia', 'rutgers', 'houston']
            bracket_16 = ['gonzaga', 'ohio', 'eastern-washington', 'iowa', 'texas-southern', 'georgetown',
                          'abilene-christian',
                          'alabama', 'north-carolina', 'winthrop', 'colgate', 'ohio-state' 'illinios',
                          'oklahoma-state', 'west-virginia', 'houston']
            bracket_8 = ['gonzaga', 'iowa', 'texas-southern', 'alabama', 'winthrop', 'colgate', 'illinios', 'houston']
            bracket_4 = ['iowa', 'alabama', 'colgate', 'illinois']
            bracket_2 = ['iowa', 'colgate']
            winner = ['colgate']
            # call function that generates bracket, returns list of teams in order to fill in bracket
            request.session['bracket_32'] = bracket_32
            request.session['bracket_16'] = bracket_16
            request.session['bracket_8'] = bracket_8
            request.session['bracket_4'] = bracket_4
            request.session['bracket_2'] = bracket_2
            request.session['winner'] = winner


            context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'bracket_32': bracket_32,
                       'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4, 'bracket_2': bracket_2,
                       'winner': winner}

    else:
        # get bracket's stats
        # assign stats to the request sessions
        request.session['bracket_32'] = bracket.bracket_32
        request.session['bracket_16'] = bracket.bracket_16
        request.session['bracket_8'] = bracket.bracket_8
        request.session['bracket_4'] = bracket.bracket_4
        request.session['bracket_2'] = bracket.bracket_2
        request.session['winner'] = bracket.winner
        request.session['stat1'] = bracket.stats[0]
        request.session['stat2'] = bracket.stats[1]
        request.session['stat3'] = bracket.stats[2]
        request.session['stat4'] = bracket.stats[3]
        request.session['stat5'] = bracket.stats[4]
        context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64}

    # naming and saving the bracket
    if request.method == 'POST' and 'name' in request.POST:
        save_form = SaveForm(request.POST)
        if save_form.is_valid():
            bracket_32 = request.session.get('bracket_32')
            bracket_16 = request.session.get('bracket_16')
            bracket_8 = request.session.get('bracket_8')
            bracket_4 = request.session.get('bracket_4')
            bracket_2 = request.session.get('bracket_2')
            winner = request.session.get('winner')
            # note to myself- it allows you to save a bracket without selecting stats, not good :(
            stat1 = request.session.get('stat1')
            stat2 = request.session.get('stat2')
            stat3 = request.session.get('stat3')
            stat4 = request.session.get('stat4')
            stat5 = request.session.get('stat5')

            stats = [stat1, stat2, stat3, stat4, stat5]
            Bracket.objects.filter.update(
                bracket_name=save_form.cleaned_data['name'],
                user=user,
                bracket_64=bracket_64,
                bracket_32=bracket_32,
                bracket_16=bracket_16,
                bracket_8=bracket_8,
                bracket_4=bracket_4,
                bracket_2=bracket_2,
                winner=winner,
                stats=stats
            )

            del request.session['stat1']
            del request.session['stat2']
            del request.session['stat3']
            del request.session['stat4']
            del request.session['stat5']
            del request.session['bracket_32']
            del request.session['bracket_16']
            del request.session['bracket_8']
            del request.session['bracket_4']
            del request.session['bracket_2']
            del request.session['winner']
            context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'save_form': save_form}

        else:
            save_form = SaveForm()
            context = {'user': user, 'user_id': user_id, 'save_form': save_form, 'bracket_64': bracket_64}

    context = {'user': user, 'user_id': user_id, 'brackets': brackets}
    return render(request, 'project/editBracket.html', context)


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

def get_school_teams():
   return pd.read_html('https://www.sports-reference.com/cbb/schools/')[0]['School'].to_list()


def get_name_link_pairs():
    req = Request("https://www.sports-reference.com/cbb/schools/")
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    links = []
    for link in soup.findAll('a'):
        sample_link = link.get('href')
        if (sample_link[0:13] == '/cbb/schools/') and (len(sample_link) > 13):
            links.append(link.get('href'))

    name_link_pairs = {}
    base_link = "https://www.sports-reference.com/cbb/schools/"[:-13]
    for link in links:
        #     name_link_pairs.append([link[13:-1], base_link + link])
        name_link_pairs.update({link[13:-1]: base_link + link})

    return name_link_pairs

def get_school_names():
    return get_name_link_pairs().keys()

def get_season_links_dict(school_name):
  if school_name not in get_school_names():
    print("school name is not valid")
  else:
    name_link_pairs = get_name_link_pairs()
    req = Request(name_link_pairs[school_name])
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")

    base_link = '/cbb/schools/' + school_name + '/'
    season_links = []
    for link in soup.findAll('a'):
    #     if (sample_link[0:13] == '/cbb/schools/') and (len(sample_link) > 13):
        sample_link = link.get('href')
        if (base_link == sample_link[0:len(base_link)]) and (sample_link[-5:] == '.html') and (sample_link[-9:-5].isnumeric()):
    #         season_links.append('https://www.sports-reference.com/cbb/schools/' + link.get('href'))
            season_links.append('https://www.sports-reference.com' + link.get('href'))

    season_links.sort()

    season_links_dict = {}

    for link in season_links:
        season_links_dict.update({link[-9:-5]: link})
    return season_links_dict

def get_2021_data():
    return pd.read_csv('bracket_2021_data.csv').set_index('Unnamed: 0')

def get_team_stats(school_name, year):
    team_stats = pd.read_html(get_season_links_dict(school_name)[year])[1]
    team_stats.set_index('Unnamed: 0', inplace=True)
    return team_stats

def get_team_stats_2021(school_name):
    team_stats = get_2021_data.loc[['school_name']]
    return team_stats

def get_school_stat_rank(school_name, year, stat_category):
    if stat_category not in get_team_stats('rutgers', '2021').columns:
        print("Not a valid stat category")
    else:
        return int(get_team_stats(school_name, year).loc['Rank'][stat_category][0][:-2])

def get_school_stat_rank_2021(school_name, stat_category):
    rank = int(get_2021_data().at[school_name, stat_category][:-2])
    return rank

def compare_school_stats(college1, college2, year, stat_category):
    if get_school_stat_rank(college1, year, stat_category) < get_school_stat_rank(college2, year, stat_category):
        return college1
    else:
        return college2

def compare_school_stats_2021(college1, college2, stat_category):
    if get_school_stat_rank_2021(college1, stat_category) < get_school_stat_rank_2021(college2, stat_category):
        return college1
    else:
        return college2


def compare_schools(school1, school2, year, stat1, stat2, stat3, stat4, stat5):
    factor1 = (1 if compare_school_stats(school1, school2, year, stat1) == school1 else -1) * 5
    factor2 = (1 if compare_school_stats(school1, school2, year, stat2) == school1 else -1) * 4
    factor3 = (1 if compare_school_stats(school1, school2, year, stat3) == school1 else -1) * 3
    factor4 = (1 if compare_school_stats(school1, school2, year, stat4) == school1 else -1) * 2
    factor5 = 1 if compare_school_stats(school1, school2, year, stat5) == school1 else -1

    sum = factor1 + factor2 + factor3 + factor4 + factor5

    if sum >= 0:
        return school1
    else:
        return school2

def compare_schools_2021(school1, school2, stat1, stat2, stat3, stat4, stat5):
    factor1 = (1 if compare_school_stats_2021(school1, school2, stat1) == school1 else -1) * 5
    factor2 = (1 if compare_school_stats_2021(school1, school2, stat2) == school1 else -1) * 4
    factor3 = (1 if compare_school_stats_2021(school1, school2, stat3) == school1 else -1) * 3
    factor4 = (1 if compare_school_stats_2021(school1, school2, stat4) == school1 else -1) * 2
    factor5 = 1 if compare_school_stats_2021(school1, school2, stat5) == school1 else -1

    sum = factor1 + factor2 + factor3 + factor4 + factor5

    if sum >= 0:
        return school1
    else:
        return school2

def next_round(bracket, year, stat1, stat2, stat3, stat4, stat5):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_schools(match[0], match[1], year, stat1, stat2, stat3, stat4, stat5))
    it = iter(temp_bracket)
    return list(zip(it, it))

def next_round_2021(bracket, stat1, stat2, stat3, stat4, stat5):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_schools_2021(match[0], match[1], stat1, stat2, stat3, stat4, stat5))
    it = iter(temp_bracket)
    return list(zip(it, it))


def next_round_test(bracket, year, stat1):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_school_stats(match[0], match[1], year, stat1))
    it = iter(temp_bracket)
    return list(zip(it, it))
