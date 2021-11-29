from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User, Group, AbstractBaseUser

class Team(models.Model):
    team_id = models.CharField(max_length=10)
    team_name = models.CharField(max_length=200)
    num_members = models.IntegerField()

    def __str__(self):
        return self.team_name

class User(models.Model):
    user_name = models.CharField(max_length=200)
    user_username = models.CharField(max_length=30)
    user_password = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    favbracket = models.ForeignKey('Bracket', on_delete=models.CASCADE, null=True, blank=True, related_name='+')

    def __str__(self):
        return self.user_name

class Bracket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    bracket_name = models.CharField(max_length=50)
    bracket = models.JSONField(default=list, blank=True, null=True)
    stats = models.JSONField(default=list, blank=True, null=True)


    def __str__(self):
        return self.bracket_name

class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title= models.CharField(max_length=500)
    content= models.CharField(max_length=500)

    def __str__(self):
        return self.content