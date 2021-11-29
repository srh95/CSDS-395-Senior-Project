from django.contrib import admin

from .models import(
    User,
    Bracket,
    Team,
    Posts
)

admin.site.register(User)
admin.site.register(Bracket)
admin.site.register(Team)
admin.site.register(Posts)
