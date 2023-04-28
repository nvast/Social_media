from django.contrib import admin
from .models import Posts, Comments, Follow

admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(Follow)
