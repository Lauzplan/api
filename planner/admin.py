from django.contrib import admin

from .models import Garden, Bed, Vegetable, COWithDate, COWithOffset, IncomingPhytosanitaire, PhytosanitaireUsage, Parcel

admin.site.register(Garden)
admin.site.register(Parcel)
admin.site.register(Bed)
admin.site.register(Vegetable)
admin.site.register(COWithOffset)
admin.site.register(COWithDate)
admin.site.register(PhytosanitaireUsage)
admin.site.register(IncomingPhytosanitaire)
