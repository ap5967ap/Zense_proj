from django.contrib import admin
from .models import IncomeObject



class AdminIncomeObject(admin.ModelAdmin):
    list_display = ('source', 'amount', 'frequency', 'last_date','next_date', 'status','added','is_active')
    list_filter = ('source', 'frequency', 'last_date', 'user')
    search_fields = ('source', 'amount', 'frequency', 'last_date', 'user')
    ordering = ('-last_date',)
admin.site.register(IncomeObject, AdminIncomeObject)