from django.contrib import admin

from .models import User, Department, Location, Event #Operator, Coordinator, Recipient,


admin.site.register(User)
admin.site.register(Department)
# admin.site.register(Operator)
# admin.site.register(Coordinator)
# admin.site.register(Recipient)
admin.site.register(Location)
admin.site.register(Event)
