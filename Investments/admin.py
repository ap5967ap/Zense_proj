from django.contrib import admin

# Register your models here.
from .models import Investment,MF

class InvestmentAdmin(admin.ModelAdmin):
    list_display=('user','year','to_invest','invested_this_year','done','risky','safe','MF','SmallCase','trade','large','mid','small','FD','SGB')
    list_filter=('user','year','done')
    search_fields=('user','year','done')
    list_editable=('done',)

class MFAdmin(admin.ModelAdmin):
    list_display=('user','name','amount','last_date','next_date')
    list_filter=('user','name','last_date','next_date')
    search_fields=('user','name','last_date','next_date')
    list_editable=('amount','last_date','next_date')
    
admin.site.register(Investment,InvestmentAdmin)
admin.site.register(MF,MFAdmin)