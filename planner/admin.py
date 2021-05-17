from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from .models import Garden, Bed, Parcel

admin.site.register(Garden)
admin.site.register(Parcel)
admin.site.register(Bed)

admin.site.register(User, UserAdmin)
