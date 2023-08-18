from django.contrib import admin
from .models import Balance
# Register your models here.
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user','balance','invest','expense','invest_p','updated')
    list_filter = ('user',)
    search_fields = ('user',)

admin.site.register(Balance,BalanceAdmin)