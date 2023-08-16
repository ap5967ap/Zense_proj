from django.contrib import admin
from .models import Manage
# Register your models here.
class ManageAdmin(admin.ModelAdmin):
    list_display = ('x','created')
admin.site.register(Manage,ManageAdmin)