from django.contrib import admin
from accounts.models import User, Admin

admin.site.register(User)
admin.site.register(Admin)
