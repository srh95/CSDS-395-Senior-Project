from django.db import models


class User(models.Model):
    user_name = models.CharField(max_length=200)
    user_username = models.CharField(max_length=30)  # username is their email
    user_password = models.CharField(max_length=50)

    def __str__(self):
        return self.user_name


class Team(models.Model):
    teamname = models.CharField(max_length=200)
    user_username = models.CharField(max_length=30)
    teamid = models.CharField(max_length=4)


