from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField(label='name', max_length=50, required=True)
    username = forms.CharField(label='username', max_length=50, required=True)
    password1 = forms.CharField(label='password', max_length=50, required=True)
    password2 = forms.CharField(label='password*', max_length=50, required=True)

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50, required=True)
    password = forms.CharField(label='Name', max_length=50, required=True)

class TeamForm(forms.Form):
    teamname = forms.CharField(label="teamname", max_length=50, required=True)
    teamid = forms.IntegerField(label="teamid", required=True)

class StatForm(forms.Form):
    stat1 = forms.CharField(label="stat1", max_length=50, required=True)
    stat2 = forms.CharField(label="stat2", max_length=50, required=True)
    stat3 = forms.CharField(label="stat3", max_length=50, required=True)
    stat4 = forms.CharField(label="stat4", max_length=50, required=True)
    stat5 = forms.CharField(label="stat5", max_length=50, required=True)

class SaveForm(forms.Form):
    name = forms.CharField(label='name', max_length=50, required=True)