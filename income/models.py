from django.db import models
from account.models import Account
choices = (('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly',
           'Monthly'), ('Yearly', 'Yearly'), ('Once', 'Once'))


class IncomeObject(models.Model):
    '''Please enter only active income'''
    '''Stores the income object'''
    source = models.CharField(max_length=255, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    frequency = models.CharField(
        max_length=255, choices=choices, blank=False, default='Monthly')
    last_date = models.DateField(blank=False)
    next_date = models.DateField(blank=False,null=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)#!Tells if the current source of income is active now(user earns through it) 
    is_passive = models.BooleanField(default=False)#!Tells if the source of income is a form of passive income
    status = models.BooleanField(default=False, blank=False, null=False)#!Default synced status
    added=models.BooleanField(default=False, blank=False, null=False)#!Income is credited
    def __str__(self):
        return self.source

    class Meta:
        ordering = ['-last_date']
        verbose_name_plural = 'Income Object'

