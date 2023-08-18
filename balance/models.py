from django.db import models
from account.models import Account

class Balance(models.Model):
    user=models.OneToOneField(Account,on_delete=models.CASCADE)
    balance=models.DecimalField(default=0, decimal_places=2,max_digits=20)
    last_month=models.DecimalField(default=0, decimal_places=2,max_digits=20)
    expense=models.DecimalField(default=0, decimal_places=2,max_digits=20)
    invest=models.DecimalField(default=0, decimal_places=2,max_digits=20)
    invest_p=models.DecimalField(default=0, decimal_places=2,max_digits=20)
    updated=models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural="Balance"