from django.contrib import admin
from .models import *

class AdminExpenseObject(admin.ModelAdmin):
    list_display=('user','date','to_expense','used_this_month','wants','needs','wants_i','needs_i')
    list_filter=('user','date')
    search_fields=('user','date')
    ordering=('-date',)
admin.site.register(Expense,AdminExpenseObject)

class AdminWants(admin.ModelAdmin):
    list_display=('user','source','amount','frequency','last_date','next_date','is_active','status','category')
    list_filter=('user','source','amount','frequency','last_date','next_date','is_active','status')
    search_fields=('user','source','amount','frequency','last_date','next_date','is_active','status')
    ordering=('-last_date',)
    
admin.site.register(Wants,AdminWants)

class AdminNeeds(admin.ModelAdmin):
    list_display=('user','source','amount','price','last_date','next_date','is_active','buy_date','amount_added','priority','remarks')
    list_filter=('user','source')
    search_fields=('user','source')
    ordering=('-last_date',)
    
admin.site.register(Needs,AdminNeeds)