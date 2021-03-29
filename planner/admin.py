from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from .models import Garden, Bed, Vegetable, COWithDate, COWithOffset, IncomingPhytosanitaire, PhytosanitaireUsage, Parcel

admin.site.register(Garden)
admin.site.register(Parcel)
admin.site.register(Bed)
admin.site.register(Vegetable)
admin.site.register(COWithOffset)
admin.site.register(COWithDate)
admin.site.register(PhytosanitaireUsage)
admin.site.register(IncomingPhytosanitaire)
admin.site.register(User, UserAdmin)
