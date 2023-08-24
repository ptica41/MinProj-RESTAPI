from django.contrib import admin

from .models import User, Department, Operator, Coordinator, Recipient, Location, Event


admin.site.register(User)
admin.site.register(Department)
admin.site.register(Operator)
admin.site.register(Coordinator)
admin.site.register(Recipient)
admin.site.register(Location)
admin.site.register(Event)
