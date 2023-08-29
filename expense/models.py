from django.db import models
from account.models import Account
from django.utils import timezone
from datetime import datetime

# Create your models here.
class Expense(models.Model):
    '''Its instance for each user will be created every month'''
    '''first month of income it will be not investing and will invest from subsequent /months'''
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    to_expense=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    used_this_month=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    wants=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    needs=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    wants_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    needs_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    date=models.DateField(default=timezone.now)
    buffer=models.DecimalField(max_digits=20,decimal_places=2,default=0) #? to be used for purchases of larger frequency as they typically have larger amount
    buffer2=models.DecimalField(max_digits=20,decimal_places=2,default=0) #? for needs Model
    def __str__(self):
        return self.user.username
    class Meta:
        ordering=['-date']
        verbose_name_plural='Expense'
    
class Wants(models.Model):
    '''Stores the wants of the user'''
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    source=models.CharField(max_length=255,blank=False)
    amount=models.DecimalField(max_digits=20,decimal_places=2,blank=False,default=0)
    frequency=models.CharField(max_length=255,choices=(('Daily','Daily'),('Weekly','Weekly'),('Monthly','Monthly'),('Quaterly','Quaterly'),('Biannually','Biannually'),('Yearly','Yearly'),('Once','Once')),blank=False,default='Monthly')
    last_date=models.DateField(blank=False)
    next_date=models.DateField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    status=models.BooleanField(default=False,blank=False,null=False)#?True if synced automatically
    category=models.CharField(max_length=255,blank=True,null=True)  

    def __str__(self):
        return self.source
    class Meta:
        ordering=['-last_date']
        verbose_name_plural='Wants'
        
        
        
class Needs(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    source=models.CharField(max_length=255,blank=False)
    amount=models.DecimalField(max_digits=20,decimal_places=2,blank=False) #!amount per month
    price=models.DecimalField(max_digits=20,decimal_places=2,blank=False) #!price of the need
    last_date=models.DateField(blank=False) #!current date when money is saved 
    next_date=models.DateField(blank=True,null=True) #!next date when money is to be saved
    buy_date=models.DateField(blank=True,null=True) #!date when the need is bought (future date)
    is_active=models.BooleanField(default=True) #!after my item is bought then it will be false
    category=models.CharField(max_length=255,blank=True,null=True) #!category of the need
    amount_added=models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True) #!amount added to the need
    priority=models.IntegerField(default=0) #!priority of the need
    remarks=models.CharField(max_length=255,blank=True,null=True) #!remarks for the need

    def __str__(self):
        return self.source
    class Meta:
        ordering=['-last_date']
        verbose_name_plural='Needs'