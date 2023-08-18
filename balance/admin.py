from django.contrib import admin
from .models import Balance
# Register your models here.
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user','balance',)

admin.site.register(Balance,BalanceAdmin)