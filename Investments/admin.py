from django.contrib import admin
from .models import Investment,MF,MFData,StockData,Stock,Other,SGB
from .mutual_fund_data import func
from .other import fd_sync


class SGBadmin(admin.ModelAdmin):
    list_display = ['user','price','date','is_active','sell_date','sell_price']
    list_filter = ['user','date','is_active']
    search_fields = ['user','date','is_active']

admin.site.register(SGB,SGBadmin)
class InvestmentAdmin(admin.ModelAdmin):
    list_display=('user','year','to_invest','invested_this_year','done','risky','safe','MF','large','mid','small','FD','SGB')
    list_filter=('user','year','done')
    search_fields=('user','year','done')
    list_editable=('done',)

class MFAdmin(admin.ModelAdmin):
    list_display=('user','name','amount','last_date','next_date','is_sip','sold')
    list_filter=('user','name','last_date','next_date')
    search_fields=('user','name','last_date','next_date')
    
class MFDataAdmin(admin.ModelAdmin):
    list_display=('name','rank','choice','d1','d2','d3','d4','d5','dmin','dmax','price','prev_return')
    list_filter=('choice',)
    search_fields=('name','rank','choice')
    
class StockDataAdmin(admin.ModelAdmin):
    list_display=('name','category','rating','buysignal','symbol')
    list_filter=('category',) 
   
   
class StockAdmin(admin.ModelAdmin):
    list_display=('name','symbol','quantity','price','is_active','user','date','category')
    list_filter=('user','date','category')
    search_fields=('user','date','category')
    list_editable=('is_active',)


class OtherAdmin(admin.ModelAdmin):
    list_display=('name','price','is_active','user','date','category')
    list_filter=('user','date','category')
    search_fields=('user','date','category')
    list_editable=('is_active',)
    
    
    
admin.site.register(Stock,StockAdmin)
admin.site.register(Investment,InvestmentAdmin)
admin.site.register(MF,MFAdmin)
admin.site.register(StockData,StockDataAdmin)
admin.site.register(MFData,MFDataAdmin)
admin.site.register(Other,OtherAdmin)
admin.site.add_action(fd_sync,name="Update FD Information")
admin.site.add_action(func,name="Update Mutual Funds Information")