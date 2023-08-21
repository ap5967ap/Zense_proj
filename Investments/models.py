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
    MF_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    SmallCase_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    trade_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    large_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)#!_i is how much invested this year
    mid_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    small_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    FD_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
    SGB_i=models.DecimalField(max_digits=20,decimal_places=2,default=0)
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
    quantity=models.IntegerField(default=1)
    last_date=models.DateField()
    next_date=models.DateField(blank=True,null=True)
    is_sip=models.BooleanField(default=False)
    sold=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user} {self.name}"
    class Meta:
        verbose_name_plural = "Mutual Fund"
        verbose_name="Mutual Fund"
        
choices=(('l','l'),('m','m'),('s','s'))
class MFData(models.Model):
    name=models.CharField(max_length=100)
    rank=models.IntegerField()
    choice=models.CharField(max_length=1,choices=choices)
    price=models.DecimalField(default=0,max_digits=20,decimal_places=2,blank=True,null=True)
    prev_return=models.DecimalField(default=0,max_digits=20,decimal_places=2,blank=True,null=True)
    d1=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    d2=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    d3=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    d4=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    d5=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    dmin=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    dmax=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    class Meta:
        verbose_name ="Mutual Fund Data"
        verbose_name_plural ="Mutual Fund Data"
        

class Stock(models.Model):
    name=models.CharField(max_length=100)
    symbol=models.CharField(max_length=100)
    quantity=models.IntegerField(default=1)
    price=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    is_active=models.BooleanField(default=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    date=models.DateField()
    category=models.CharField(max_length=100,choices=(('l','l'),('m','m'),('s','s')))
    sell_price=models.DecimalField(default=0,max_digits=20,decimal_places=2,blank=True,null=True)
    def __str__(self):
        return f"{self.user} {self.name}"
    class Meta:
        verbose_name_plural = "Stock"
        verbose_name="Stock"

class StockData(models.Model):
    name=models.CharField(max_length=100)
    symbol=models.CharField(max_length=100)
    nifty50=models.BooleanField(default=False)
    niftybank=models.BooleanField(default=False)
    niftyit=models.BooleanField(default=False)
    niftyfmcg=models.BooleanField(default=False)
    niftypharma=models.BooleanField(default=False)
    niftyauto=models.BooleanField(default=False)
    niftyenergy=models.BooleanField(default=False)
    niftynext50=models.BooleanField(default=False)
    niftyhealthcare=models.BooleanField(default=False)
    category=models.CharField(max_length=100,choices=(('l','l'),('m','m'),('s','s'),('n','n')))
    price=models.DecimalField(default=0,max_digits=20,decimal_places=2,blank=True,null=True)
    ESG=models.IntegerField(default=0)#!risky
    ma50=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    ma200=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    pe=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    pb=models.DecimalField(default=0,max_digits=20,decimal_places=2)#?price to book
    roe=models.DecimalField(default=0,max_digits=20,decimal_places=2)#?return on equity
    doe=models.DecimalField(default=0,max_digits=20,decimal_places=2)#?debt to equity   
    enterpriseToEbitda=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    week52low=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    week52high=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    dividendYield=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    rsi=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    ta=models.CharField(max_length=100,choices=(('b','b'),('s','s'),('n','n'),('sb','sb'),('ss','ss')),default='n')
    rating=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    buysignal=models.DecimalField(default=0,max_digits=20,decimal_places=2)
    class Meta:
        verbose_name_plural = "Stock Data"
        verbose_name="Stock Data"