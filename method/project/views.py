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
from itertools import combinations
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

# checks whether the march madness tournament has started
def isTournamentStarted():
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

# view for home page
def home(request):
    return render(request, 'project/home.html')

# view for creating a team
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

# view for joining a team
def joinTeam(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    form = JoinTeamForm(request.POST)
    brackets = Bracket.objects.filter(user__pk=user_id)
    context = {'user': user, 'brackets': brackets}
    if request.method == 'GET' and 'join_code' in request.GET:
        code = request.GET.get('join_code')
        try:
            team_obj = Team.objects.get(team_id=code)
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

        except ObjectDoesNotExist:
            messages.error(request, 'This join code is invalid.')
            url = '/joinTeam/' + str(user_id)
            return HttpResponseRedirect(url)
    else:
        form = JoinTeamForm()
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'form': form}
        return render(request, 'project/joinTeam.html', context)

# removes user from team
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

# view for sign up page
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

# view for log in page
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

# view for home page when logged in
def user_home(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    create = isTournamentStarted()
    context = {'user': user, 'user_id': user_id, 'create': create}
    return render(request, 'project/userHome.html', context)

# view for news page
def news(request):
    allposts = Posts.objects.all()
    context = {'allposts': allposts}
    return render(request, 'project/News.html', context)

# view for new page when logged in
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

# view for teams page when logged in
def userTeams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    favbracketname = user.favbracket
    brackets = Bracket.objects.filter(bracket_name=favbracketname)
    edit = isTournamentStarted()
    if user.team:
        team_obj = get_object_or_404(Team, team_id=user.team.team_id)
        teammates = User.objects.filter(team=team_obj)
        num_teammates = len(teammates)
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'teammates': teammates,
                   'num_teammates': num_teammates, 'edit': edit}
        return render(request, 'project/userTeams.html', context)
    else:
        context = {'user': user, 'user_id': user_id}
        return render(request, 'project/userTeams.html', context)

# view for teams page
def teams(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    favbracketname = user.favbracket
    brackets = Bracket.objects.filter(bracket_name=favbracketname)
    edit = isTournamentStarted()
    if user.team:
        team_obj = get_object_or_404(Team, team_id=user.team.team_id)
        teammates = User.objects.filter(team=team_obj)
        num_teammates = len(teammates)
        context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'teammates': teammates,
                   'num_teammates': num_teammates, 'edit': edit}
        return render(request, 'project/teams.html', context)
    else:
        context = {'user': user, 'user_id': user_id, 'edit': edit}
    return render(request, 'project/teams.html', context)

# generates first round of teams for 2021
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

        # remove nones from the list
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
        else:
            # append nones back 5-length to tell how many
            num_nones = 5-len(ordered_stats)
            i = 0
            while i < num_nones:
                ordered_stats.append("None")
                i += 1

            # pass ordered_stats into function
            b_32, bracket_32 = next_round_2021(bracket_2021, stat1, stat2, stat3, stat4, stat5)
            b_16, bracket_16 = next_round_2021(b_32, stat1, stat2, stat3, stat4, stat5)
            b_8, bracket_8 = next_round_2021(b_16, stat1, stat2, stat3, stat4, stat5)
            b_4, bracket_4 = next_round_2021(b_8, stat1, stat2, stat3, stat4, stat5)
            b_2, bracket_2 = next_round_2021(b_4, stat1, stat2, stat3, stat4, stat5)
            winner = compare_schools_2021(b_2[0][0], b_2[0][1], stat1, stat2, stat3, stat4, stat5)
            print(b_32)


            request.session['bracket_32'] = bracket_32
            request.session['bracket_16'] = bracket_16
            request.session['bracket_8'] = bracket_8
            request.session['bracket_4'] = bracket_4
            request.session['bracket_2'] = bracket_2
            request.session['winner'] = winner

            context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'bracket_32': bracket_32,
                       'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4, 'bracket_2': bracket_2,
                       'winner': winner, 'ordered_stats': ordered_stats}

    else:
        context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64}

    # naming and saving the bracket
    if request.method == 'POST' and 'name' in request.POST:
        print("request went through")
        save_form = SaveForm(request.POST)
        if save_form.is_valid():
            print('form is valid')
            try:
                bracket_32 = request.session.get('bracket_32')
                bracket_16 = request.session.get('bracket_16')
                bracket_8 = request.session.get('bracket_8')
                bracket_4 = request.session.get('bracket_4')
                bracket_2 = request.session.get('bracket_2')
                winner = request.session.get('winner')
                # note- it allows you to save a bracket without selecting stats, not good :(
                stat1 = request.session.get('stat1')
                stat2 = request.session.get('stat2')
                stat3 = request.session.get('stat3')
                stat4 = request.session.get('stat4')
                stat5 = request.session.get('stat5')

                stats = [stat1, stat2, stat3, stat4, stat5]

                # display bracket score
                # maybe have a check so that scores only show up
                score = calculateScore(bracket_32, bracket_16, bracket_8, bracket_4, bracket_2, winner)

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
                    stats=stats,
                    score=score
                )
                database.save()
                print(score)

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

# view for viewing user's brackets
def myBracket(request, user_id):
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

    context = {'user': user, 'user_id': user_id, 'brackets': brackets, 'edit': edit}
    return render(request, 'project/bracket.html', context)

def calculateScore(bracket_32, bracket_16, bracket_8, bracket_4, bracket_2, winner):
    actual_32 = ['gonzaga',
                       'oklahoma',
                       'creighton',
                       'ohio',
                       'southern-california',
                       'kansas',
                       'oregon',
                       'iowa',
                       'michigan',
                       'louisiana-state',
                       'colorado',
                       'florida-state',
                       'ucla',
                       'abilene-christian',
                       'maryland',
                       'alabama',
                       'baylor',
                       'wisconsin',
                       'villanova',
                       'north-texas',
                       'texas-tech',
                       'arkansas',
                       'florida',
                       'oral-roberts',
                       'illinois',
                       'loyola-il',
                       'oregon-state',
                       'oklahoma-state',
                       'syracuse',
                       'west-virginia',
                       'rutgers',
                       'houston']

    actual_16 = ['gonzaga',
                       'creighton',
                       'southern-california',
                       'oregon',
                       'michigan',
                       'florida-state',
                       'ucla',
                       'alabama',
                       'baylor',
                       'villanova',
                       'arkansas',
                       'oral-roberts',
                       'loyola-il',
                       'oregon-state',
                       'syracuse',
                       'houston']

    actual_8 = ['gonzaga',
                      'southern-california',
                      'michigan',
                      'ucla',
                      'baylor',
                      'arkansas',
                      'oregon-state',
                      'houston']

    actual_4 = ['gonzaga',
                      'ucla',
                      'baylor',
                      'houston']

    actual_2 = ['gonzaga', 'baylor']

    actual_winner = 'baylor'

    score32 = len([team for team in bracket_32 if team in actual_32])
    score16 = 2*len([team for team in bracket_16 if team in actual_16])
    score8 = 4*len([team for team in bracket_8 if team in actual_8])
    score4 = 8*len([team for team in bracket_4 if team in actual_4])
    score2 = 16*len([team for team in bracket_2 if team in actual_2])
    score = score32+score16+score8+score4+score2

    if winner in actual_winner:
        score += 32

    return score

# view for edit bracket
def editBracket(request, bracket_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    brackets = Bracket.objects.filter(id=bracket_id)
    bracket = brackets[0]
    # get bracket's info
    bracket_32 = bracket.bracket_32
    bracket_16 = bracket.bracket_16
    bracket_8 = bracket.bracket_8
    bracket_4 = bracket.bracket_4
    bracket_2 = bracket.bracket_2
    winner = bracket.winner
    stat_list = bracket.stats
    brack_name = bracket.bracket_name

    bracket_64, bracket_2021 = generate2021Teams()
    # choosing the stats
    if request.method == 'GET':
        if 'stat1' in request.GET:
            stat1 = request.GET.get('stat1')
        else:
            stat1 = bracket.stats[0]
        if 'stat2' in request.GET:
            stat2 = request.GET.get('stat2')
        else:
            stat2 = bracket.stats[1]
        if 'stat3' in request.GET:
            stat3 = request.GET.get('stat3')
        else:
            stat3 = bracket.stats[2]
        if 'stat4' in request.GET:
            stat4 = request.GET.get('stat4')
        else:
            stat4 = bracket.stats[3]
        if 'stat5' in request.GET:
            stat5 = request.GET.get('stat5')
        else:
            stat5 = bracket.stats[4]

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
        else:
            # append nones back 5-length to tell how many
            num_nones = 5 - len(ordered_stats)
            i = 0
            while i < num_nones:
                ordered_stats.append("None")
                i += 1

            stat_list = ordered_stats
            # pass ordered_stats into function
            b_32, bracket_32 = next_round_2021(bracket_2021, stat1, stat2, stat3, stat4, stat5)
            b_16, bracket_16 = next_round_2021(b_32, stat1, stat2, stat3, stat4, stat5)
            b_8, bracket_8 = next_round_2021(b_16, stat1, stat2, stat3, stat4, stat5)
            b_4, bracket_4 = next_round_2021(b_8, stat1, stat2, stat3, stat4, stat5)
            b_2, bracket_2 = next_round_2021(b_4, stat1, stat2, stat3, stat4, stat5)
            winner = compare_schools_2021(b_2[0][0], b_2[0][1], stat1, stat2, stat3, stat4, stat5)

            request.session['bracket_32'] = bracket_32
            request.session['bracket_16'] = bracket_16
            request.session['bracket_8'] = bracket_8
            request.session['bracket_4'] = bracket_4
            request.session['bracket_2'] = bracket_2
            request.session['winner'] = winner

            context = {'bracket': bracket, 'user': user, 'user_id': user_id, 'bracket_64': bracket_64,
                       'bracket_32': bracket_32, 'bracket_16': bracket_16, 'bracket_8': bracket_8,
                       'bracket_4': bracket_4, 'bracket_2': bracket_2,'winner': winner, 'name': brack_name,
                       'stats': stat_list}


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
                stat1 = request.session.get('stat1')
                stat2 = request.session.get('stat2')
                stat3 = request.session.get('stat3')
                stat4 = request.session.get('stat4')
                stat5 = request.session.get('stat5')

                stats = [stat1, stat2, stat3, stat4, stat5]
                Bracket.objects.filter(id=bracket_id).update(
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

                brack_name = save_form.cleaned_data['name']
                context = {'bracket': bracket, 'user': user, 'user_id': user_id, 'bracket_64': bracket_64,
                           'bracket_32': bracket_32,
                           'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4,
                           'bracket_2': bracket_2,
                           'winner': winner, 'stats': stats, 'name': brack_name}
            except:
                bracket_32 = bracket.bracket_32
                bracket_16 = bracket.bracket_16
                bracket_8 = bracket.bracket_8
                bracket_4 = bracket.bracket_4
                bracket_2 = bracket.bracket_2
                winner = bracket.winner
                stat_list = bracket.stats
                Bracket.objects.filter(id=bracket_id).update(
                    bracket_name=save_form.cleaned_data['name'],
                    user=user,
                    bracket_64=bracket_64,
                    bracket_32=bracket_32,
                    bracket_16=bracket_16,
                    bracket_8=bracket_8,
                    bracket_4=bracket_4,
                    bracket_2=bracket_2,
                    winner=winner,
                    stats=stat_list
                )
                brack_name = save_form.cleaned_data['name']
                context = {'bracket': bracket, 'user': user, 'user_id': user_id, 'bracket_64': bracket_64,
                           'bracket_32': bracket_32,
                           'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4,
                           'bracket_2': bracket_2,
                           'winner': winner, 'stats': stat_list, 'name': brack_name}
                print(winner)
                print(stat_list)


        else:
            save_form = SaveForm()
            context = {'bracket': bracket, 'user': user, 'user_id': user_id, 'save_form': save_form}
    else:
        context = {'bracket': bracket, 'user': user, 'user_id': user_id, 'bracket_64': bracket_64,
                   'bracket_32': bracket_32, 'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4,
                   'bracket_2': bracket_2, 'winner': winner, 'stats': stat_list, 'name': brack_name}

    return render(request, 'project/editBracket.html', context)

def prediction(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    bracket_64, bracket_2021 = generate2021Teams()

    stat1 = "FTA"
    stat2 = "2P"
    stat3 = "PTS"
    stat4 = "FT%"
    stat5 = "3P"

    list_stats = ["Free Throw Attempts", "2-Point Field Goals Per Game", "Points Per Game", "Free Throw Percentage",
                  "3-Point Field Goals Per Game"]

    # pass ordered_stats into function
    b_32, bracket_32 = next_round_2021(bracket_2021, stat1, stat2, stat3, stat4, stat5)
    b_16, bracket_16 = next_round_2021(b_32, stat1, stat2, stat3, stat4, stat5)
    b_8, bracket_8 = next_round_2021(b_16, stat1, stat2, stat3, stat4, stat5)
    b_4, bracket_4 = next_round_2021(b_8, stat1, stat2, stat3, stat4, stat5)
    b_2, bracket_2 = next_round_2021(b_4, stat1, stat2, stat3, stat4, stat5)
    winner = compare_schools_2021(b_2[0][0], b_2[0][1], stat1, stat2, stat3, stat4, stat5)

    hideScore = isTournamentStarted()
    score = calculateScore(bracket_32, bracket_16, bracket_8, bracket_4, bracket_2, winner)

    context = {'user': user, 'user_id': user_id, 'bracket_64': bracket_64, 'bracket_32': bracket_32,
                       'bracket_16': bracket_16, 'bracket_8': bracket_8, 'bracket_4': bracket_4, 'bracket_2': bracket_2,
                       'winner': winner, 'list_stats': list_stats, 'score': score, 'hideScore': hideScore}

    return render(request, 'project/prediction.html', context)



# scrape for tournament game info
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

# view for scores page
def scores(request):
    [teamL, teamW, imgsL] = scoreScrape()
    context = {'teamL': teamL, 'teamW': teamW, 'img_name': json.dumps(imgsL)}
    return render(request, 'project/scores.html', context)

# view for scores page when logged in
def userScores(request, user_id):
    [teamL, teamW, imgsL] = scoreScrape()
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user, 'user_id': user_id, 'teamL': teamL, 'teamW': teamW, 'img_name': imgsL}
    return render(request, 'project/userScores.html', context)


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
    factor2 = 0 if stat2 == "None" else ((1 if compare_school_stats_2021(school1, school2, stat2) == school1 else -1) * 4)
    factor3 = 0 if stat3 == "None" else ((1 if compare_school_stats_2021(school1, school2, stat3) == school1 else -1) * 3)
    factor4 = 0 if stat4 == "None" else ((1 if compare_school_stats_2021(school1, school2, stat4) == school1 else -1) * 2)
    factor5 = 0 if stat5 == "None" else (1 if compare_school_stats_2021(school1, school2, stat5) == school1 else -1)

    sum = factor1 + factor2 + factor3 + factor4 + factor5

    if sum >= 0:
        return school1
    else:
        return school2

def next_round(bracket, year, stat1, stat2, stat3, stat4, stat5):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_schools(match[0], match[1], year, stat1, stat2, stat3, stat4, stat5))
    bracket = temp_bracket
    it = iter(temp_bracket)
    return list(zip(it, it)), bracket

def next_round_2021(bracket, stat1, stat2, stat3, stat4, stat5):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_schools_2021(match[0], match[1], stat1, stat2, stat3, stat4, stat5))
    bracket = temp_bracket
    it = iter(temp_bracket)
    return list(zip(it, it)), bracket


def next_round_test(bracket, year, stat1):
    temp_bracket = []
    for match in bracket:
        temp_bracket.append(compare_school_stats(match[0], match[1], year, stat1))
    it = iter(temp_bracket)
    return list(zip(it, it))
