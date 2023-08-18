from django.contrib import admin
from .models import Investment,MF,MFData
from .mutual_fund_data import func

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
    
class MFDataAdmin(admin.ModelAdmin):
    list_display=('name','rank','choice','d1','d2','d3','d4','d5','dmin','dmax')
    list_filter=('choice',)
    search_fields=('name','rank','choice')
admin.site.register(Investment,InvestmentAdmin)
admin.site.register(MF,MFAdmin)
admin.site.register(MFData,MFDataAdmin)
admin.site.add_action(func,name="Update Mutual Funds Information")