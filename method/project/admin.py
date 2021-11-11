from django.contrib import admin

from .models import(
    User,
    Bracket
)

admin.site.register(User)
admin.site.register(Bracket)
