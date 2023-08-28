import decimal
from django.contrib import messages
from .models import *
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from expense.models import Expense
from balance.models import Balance
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
@login_required(login_url='/account/login')
def FD_home(request):
    user=request.user
    fd=Other.objects.filter(user=user,category='FD')
    investment=Investment.objects.get(user=user,year=datetime.now().year)
    return render(request,'FD_home.html',{'fd':fd,'inv':investment})

@login_required(login_url='/account/login')
def SGB_home(request):
    user=request.user
    sgb=SGB.objects.filter(user=user)
    investment=Investment.objects.get(user=user,year=datetime.now().year)
    dd=datetime.now().date()
    return render(request,'sgb_home.html',{'fd':sgb,'inv':investment,'dd':dd})

@login_required(login_url='/account/login')
def SGB_buy(request):
    user=request.user
    if request.method=="POST":
        price=float(request.POST.get('price'))
        date=datetime.strptime(request.POST.get('date'),'%Y-%m-%d')
        duration=int(request.POST.get('duration'))
        SGB.objects.create(user=user,price=price,date=date,duration=duration,sell_date=date+timedelta(days=365*duration))
        inv=Investment.objects.get(user=user,year=datetime.now().year)
        inv.SGB_i+=decimal.Decimal(price)
        inv.invested_this_year+=decimal.Decimal(price)
        inv.save()
        bal=Balance.objects.get(user=user)
        bal.balance-=decimal.Decimal(price)
        bal.save()
        return redirect('sgb_home')
    return render(request, 'sgb_buy.html')
        
def SGB_sell(request):
    user=request.user
    if request.method=='POST':
        id=request.POST.get('id')
        sell_price=float(request.POST.get('sell_price'))
        sgb=SGB.objects.get(user=user,id=id)
        if sgb.sell_date >= datetime.now().date():
            e1='SGB can be sold only after maturity'
            return render(request,'sgb_sell.html',{'e1':e1})
        else:
            sgb.sell_price=sell_price
            sgb.is_active=False
            sgb.save() 
            i=sgb
            bal=Balance.objects.get(user=i.user)
            bal.balance+=decimal.Decimal(i.sell_price)
            bal.save()
            balance=bal
            user=i.user
            balance.expense+=i.sell_price*decimal.Decimal(0.70)
            balance.invest+=i.sell_price*decimal.Decimal(0.30)
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            inv.to_invest+=decimal.Decimal(i.sell_price*decimal.Decimal(0.30))
            inv.save()
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            age=datetime.now().year-user.dob.year
            to_invest=inv.to_invest
            inv.safe=age
            inv.risky=100-inv.safe
            inv.save()
            inv.MF=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(20/100)
            inv.large=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(40/100)
            inv.mid=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(15/100)
            inv.small=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(10/100)
            inv.FD=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(60/100)
            inv.SGB=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(40/100)
            inv.save()
            inv=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
            inv.to_expense += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))
            inv.wants += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))*decimal.Decimal(0.60)
            inv.needs += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))*decimal.Decimal(0.40)
            inv.save()
            return redirect('sgb_home')
    else:
        sgb=SGB.objects.filter(user=user,is_active=True, sell_date__lte=datetime.now().date())
        return render(request,'sgb_sell.html',{'sgb':sgb})
        
    


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
        inv=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
        inv.to_expense+=decimal.Decimal(fd.sell_price)
        inv.wants+=decimal.Decimal(fd.sell_price)
        inv.save() 
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
            balance=bal
            user=i.user
            balance.expense+=i.sell_price*decimal.Decimal(0.70)
            balance.invest+=i.sell_price*decimal.Decimal(0.30)
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            inv.to_invest+=decimal.Decimal(i.sell_price*decimal.Decimal(0.30))
            inv.save()
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            age=datetime.now().year-user.dob.year
            to_invest=inv.to_invest
            inv.safe=age
            inv.risky=100-inv.safe
            inv.save()
            inv.MF=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(20/100)
            inv.large=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(40/100)
            inv.mid=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(15/100)
            inv.small=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(10/100)
            inv.FD=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(60/100)
            inv.SGB=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(40/100)
            inv.save()
            inv=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
            inv.to_expense += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))
            inv.wants += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))*decimal.Decimal(0.60)
            inv.needs += decimal.Decimal(i.sell_price*decimal.Decimal(0.70))*decimal.Decimal(0.40)
            inv.save()
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
