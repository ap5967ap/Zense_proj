from django.contrib import admin
# Register your models here.
from .models import Account
class AccountAdmin(admin.ModelAdmin):
    list_display = ('email','username','first_name','last_name','phone','dob','pan','date_joined','last_login','is_staff','is_active')
    search_fields = ('email','username','first_name','last_name','phone','dob','pan')
    readonly_fields=('date_joined','last_login','password','pan')
admin.site.register(Account,AccountAdmin)