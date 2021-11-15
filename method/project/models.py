from django.db import models
from django.contrib.auth.models import User, Group

class Team(models.Model):
    team_id = models.CharField(max_length=8)
    team_name = models.CharField(max_length=200)
    num_members = models.CharField(max_length=2)


class User(models.Model):
    user_name = models.CharField(max_length=200)
    user_username = models.CharField(max_length=30)  # username is their email
    user_password = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user_name


class Bracket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    bracket_name = models.CharField(max_length=50)
    bracket = models.JSONField(default=list, blank=True, null=True)
    stat1 = models.CharField(max_length=50)
    stat2 = models.CharField(max_length=50)
    stat3 = models.CharField(max_length=50)
    stat4 = models.CharField(max_length=50)
    stat5 = models.CharField(max_length=50)

    def __str__(self):
        return self.bracket_name