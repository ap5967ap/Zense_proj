from datetime import datetime, timedelta
import decimal
from django.shortcuts import render
from .models import Balance
from expense.models import Expense
from Investments.models import Investment
from account.models import Account
from expense.models import Expense,Needs,Wants
from Investments.models import Investment,MF,Stock,Other,SGB,StockData
from income.models import IncomeObject
from django.db.models import Sum
import random


def balance(request):
    user=request.user
    balance = Balance.objects.get(user=user)
    expense = Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
    inv=Investment.objects.get(user=user,year=datetime.now().year)
    bal=balance.balance
    allowed=balance.expense
    spent_in_wants=expense.wants_i
    spent_in_needs=expense.needs_i
    amount_left_in_wants=expense.wants
    amount_left_in_needs=expense.needs
    buffer_wants=expense.buffer
    buffer_needs=expense.buffer2
    spent_this_month=expense.used_this_month
    to_invest=inv.to_invest
    invested_this_year=inv.invested_this_year
    # more_inv_details=link
    return render(request, 'balance.html', {
        'bal':bal,
        'allowed':allowed,
        'spent_in_wants':spent_in_wants,
        'spent_in_needs':spent_in_needs,
        'amount_left_in_wants':amount_left_in_wants,
        'amount_left_in_needs':amount_left_in_needs,
        'buffer_wants':buffer_wants,
        'buffer_needs':buffer_needs,
        'spent_this_month':spent_this_month,
        'to_invest':to_invest,
        'invested_this_year':invested_this_year,
        
    })
    
def profile(request):
    user=request.user
    acc=Account.objects.get(username=user.username)
    return render(request, 'profile.html', {'acc':acc})