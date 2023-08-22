import decimal
from django.contrib import messages
from .models import *
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from balance.models import Balance
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
@login_required(login_url='/account/login')
def FD_home(request):
    user=request.user
    fd=Other.objects.filter(user=user,category='FD')
    investment=Investment.objects.filter(user=user,year=datetime.now().year)
    return render(request,'FD_home.html',{'fd':fd,'inv':investment})



@login_required(login_url='/account/login')
def FD_buy(request):
    user=request.user
    if request.method=="POST":
        name=request.POST.get('name')
        price=request.POST.get('price')
        date=request.POST.get('date')
        interest=request.POST.get('interest')
        sell_date=request.POST.get('sell_date')
        years=((datetime.strptime(sell_date,"%Y-%m-%d")-(datetime.strptime(date,"%Y-%m-%d"))).days)/365
        sell_price=float(price)*(1+float(interest)/100)**years
        Other.objects.create(name=name,price=price,date=date,interest=interest,sell_date=sell_date,sell_price=sell_price,user=user,category='FD')
        inv=Investment.objects.get(user=user,year=datetime.now().year)
        inv.FD_i+=decimal.Decimal(price)
        inv.invested_this_year+=decimal.Decimal(price)
        inv.save()
        bal=Balance.objects.get(user=user)
        bal.balance-=decimal.Decimal(price)
        bal.save()
        return redirect('fd_home')
    return render(request,'fd_buy.html')

@login_required(login_url='/account/login')
def FD_sell(request):
    user=request.user
    if request.method=="POST":
        name=request.POST.get('name')
        fd=Other.objects.get(user=user,name=name,category='FD',is_active=True)
        sell_date=request.POST.get('sell_date')
        sell_price=request.POST.get('sell_price')
        fd.sell_date=sell_date
        fd.sell_price=sell_price
        fd.is_active=False
        fd.save()
        bal=Balance.objects.get(user=user)
        bal.balance+=decimal.Decimal(fd.sell_price)
        bal.save()
        ... #!EXPENSE
        return redirect('fd')
    else:
        messages.warning(request,'Consider using user current balance and emerency fund and try avoiding selling FD before maturity.')
        fd=Other.objects.filter(user=user,category='FD',is_active=True)
    return render(request,'fd_sell.html',{'fd':fd})

def fd_sync(*args,**kwargs):
    try:
        fd=Other.objects.filter(category='FD',is_active=True,sell_date=datetime.now().date())
        for i in fd:
            i.is_active=False
            i.save()
            bal=Balance.objects.get(user=i.user)
            bal.balance+=decimal.Decimal(i.sell_price)
            bal.save()
            ...#!Investment
            #TODOExpense
            subject=f'FD {i.name} matured'
            message=render_to_string('fd_sold.html',{'user':i.user,'amount':i.price,'name':i.name,'s':i.sell_price})
            email=EmailMessage(subject,message,to=[i.user.email])
            try:
                email.send()
            except:
                with open('cron_log.log','a') as file:
                    file.write(f"Email not sent to {i.user.email} on {datetime.now().date()} for SIP \n")
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')  
