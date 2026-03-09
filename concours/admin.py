from django.contrib import admin
from .models import Module, Concours, SessionConcours

admin.site.register(Module)
admin.site.register(Concours)
admin.site.register(SessionConcours)