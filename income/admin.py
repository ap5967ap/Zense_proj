from datetime import timedelta
from django.contrib import admin
from .models import IncomeObject
from .views import _re
class AdminIncomeObject(admin.ModelAdmin):
    list_display = ('source', 'amount', 'frequency', 'last_date','next_date', 'status')
    list_filter = ('source', 'amount', 'frequency', 'last_date', 'user')
    search_fields = ('source', 'amount', 'frequency', 'last_date', 'user')
    ordering = ('-last_date',)
admin.site.register(IncomeObject, AdminIncomeObject)