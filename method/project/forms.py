from django import forms
from .models import (
    User, Bracket, Team
)

class RegisterForm(forms.Form):
    name = forms.CharField(label='name', max_length=50, required=True)
    username = forms.CharField(label='username', max_length=50, required=True)
    password1 = forms.CharField(label='password', max_length=50, required=True)
    password2 = forms.CharField(label='password*', max_length=50, required=True)

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50, required=True)
    password = forms.CharField(label='Name', max_length=50, required=True)

class TeamForm(forms.Form):
    team_name = forms.CharField(label="team_name", max_length=50, required=True)
    num_members = forms.IntegerField(label="num_members", required=True)
    formbracket = forms.CharField(label="bracket_name", max_length=20, required=True)

class JoinTeamForm(forms.Form):
    code = forms.CharField(label="code", max_length=10, required=True)
    formbracket = forms.CharField(label="bracket_name", max_length=20, required=True)

class StatForm(forms.Form):
    stat1 = forms.CharField(label="stat1", max_length=50, required=True)
    stat2 = forms.CharField(label="stat2", max_length=50, required=True)
    stat3 = forms.CharField(label="stat3", max_length=50, required=True)
    stat4 = forms.CharField(label="stat4", max_length=50, required=True)
    stat5 = forms.CharField(label="stat5", max_length=50, required=True)

class SaveForm(forms.Form):
    name = forms.CharField(label='bracketname', max_length=50, required=True)
