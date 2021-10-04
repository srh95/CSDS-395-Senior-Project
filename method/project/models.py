from django.db import models

class User(models.Model):
    user_name = models.CharField(max_length=200)
    user_username = models.CharField(max_length=30)
    user_password = models.CharField(max_length=50)

    def __str__(self):
        return self.restaurant_name


class