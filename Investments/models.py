from django.db import models
from account.models import Account
from datetime import datetime

class Investment(models.Model): 
    '''Its instance for each user will be created every year'''
    '''first year of income it will be not investing and will invest from subsequent years'''
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    to_invest=models.DecimalField(max_digits=20,decimal_places=2) #TODO income me i add it to passive when i sell 
    #TODO I WILL REINVEST THAT AMOUNT as my expenses are covered by active income
    #TODO I will add the amount i got by selling to to_invest
    invested_this_year=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    year=models.IntegerField(default=datetime.now().year)
    done=models.BooleanField(default=False)
    risky=models.IntegerField()#!stored in %
    safe=models.IntegerField()#!stored in %
    MF=models.IntegerField() #!Stored in currency
    SmallCase=models.IntegerField() #!Stored in currency 
    trade=models.IntegerField(default=0) #!Stored in currency
    large=models.IntegerField() #!Stored in currency
    mid=models.IntegerField() #!Stored in currency
    small=models.IntegerField() #!Stored in currency
    FD=models.IntegerField() #!Stored in currency
    SGB=models.IntegerField() #!Stored in currency
    def __str__(self):
        return f"{self.user} {self.year}"
    class Meta:
        verbose_name_plural = "Investment"

class MF(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=20,decimal_places=2)
    last_date=models.DateField()
    next_date=models.DateField()
    def __str__(self):
        return f"{self.user} {self.name}"
    class Meta:
        verbose_name_plural = "Mutual Fund"
        verbose_name="Mutual Fund"
        
