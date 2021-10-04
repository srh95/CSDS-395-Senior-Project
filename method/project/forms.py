from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField(label='name',max_length=50, required=True)
    username = forms.CharField(label='username', max_length=50, required=True)
    password1 = forms.CharField(label='password', max_length=50, required=True)
    password2 = forms.CharField(label='password*', max_length=50, required=True)

class LoginForm(forms.Form):
    username = forms.CharField(label='username',max_length=50, required=True)
    password = forms.CharField(label='Name', max_length=50, required=True)