import decimal
import json
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from .models import MF,Investment,MFData
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .mutual_fund_data import prediction
from balance.models import Balance
import yfinance as yf
from income.analysis import get_inflation
from django.db.models import Sum
from django.contrib import messages

def _yearly_average_buying_price(l):
    x=0
    for i in l:
        x+=i.amount*i.quantity
    return x/len(l)


@login_required(login_url='/account/login/')
def mf_data_single(request,name):
    l=MF.objects.filter(name=name,user=request.user).order_by('last_date')
    start_year=l[0].last_date.year
    end_year=datetime.now().year
    dict=[]
    for i in range(start_year,end_year+1):
        try:
            dict.append((_yearly_average_buying_price(l.filter(last_date__year=i))-_yearly_average_buying_price(l.filter(last_date__year=i-1)))/_yearly_average_buying_price(l.filter(last_date__year=i-1))*100)
        except ZeroDivisionError:
            dict.append(0)
    inflation_dict=get_inflation()
    infla=[]
    labels=[]
    co=0
    for i in range(start_year,end_year+1):
        labels.append(i)
        try:
            infla.append(float(inflation_dict[i]))
        except KeyError:
            try:
                infla.append(infla[co-1])
            except:
                infla.append(0)
        co+=1
    return JsonResponse(data={
                            'dict':dict,
                            'infla':infla,
                            'labels':labels,
                            })





@login_required(login_url='/account/login/')
def mf_prev(request):
    user=request.user
    l=Investment.objects.filter(user=user).order_by('year')
    mf=[]
    year=[]
    for i in l:
        mf.append(float(i.MF_i))
        year.append(int(i.year))
    return JsonResponse(data={'mf':mf,'year':year})


@login_required(login_url='/account/login/')
def mf_sell(request):
    user=request.user
    if request.method=='POST':
        name=request.POST.get('name')
        bought=MF.objects.filter(user=user,sold=False,name=name).exists()
        if not bought:
            messages.error(request,'You have not bought this MF')
            return redirect('mf_sell')
        amount=float(request.POST.get('amount'))
        date=request.POST.get('date')
        cho=request.POST.get('type')
        l=MF.objects.filter(user=user,sold=False,name=name)
        qty=0
        for i in l:
            qty+=i.quantity
            i.sold=True
            i.save()
        obj=MF.objects.create(user=user,name=name,amount=amount/qty,quantity=qty,last_date=date,sold=True,is_sip=False)
        obj.save()
        bal=Balance.objects.get(user=user)
        bal.balance+=decimal.Decimal(amount)
        bal.save()
        inv=Investment.objects.get(user=user,year=datetime.now().year)
        inv.to_invest+=decimal.Decimal(amount)
        inv.save()
        if cho=='1':
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            age=datetime.now().year-user.dob.year
            to_invest=inv.to_invest
            inv.safe=age
            inv.risky=100-inv.safe
            inv.MF=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(20/100)
            inv.SmallCase=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(15/100)
            if age <50:
                inv.trade=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(10/100)
                inv.large=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(33/100)
                inv.mid=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(14/100)
                inv.small=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(8/100)
            else:
                inv.trade=0
                inv.large=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(40/100)
                inv.mid=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(15/100)
                inv.small=decimal.Decimal(inv.risky/100)*to_invest*decimal.Decimal(10/100)
            inv.FD=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(60/100)
            inv.SGB=decimal.Decimal(inv.safe/100)*to_invest*decimal.Decimal(40/100)
            inv.save()
        elif cho=='2':
            ...
            #TODO: add to expense
        return redirect('mf_home')
        
    else:
        l=MF.objects.filter(user=user,sold=False)
        l_unique=[]
        dict={}
        with open('codes.json') as file:
            dict=json.load(file)
        dict2={key: value for d in dict for value, key in d.items()}
        name=''
        try:
            name=request.GET.get('name')
            price=decimal.Decimal(yf.download(str(dict2.get(name))+".BO",period='1d')['Close'].iloc[0])
        except:
            pass
        qty=0
        obb=MF.objects.filter(user=user,name=name,sold=False)
        for i in obb:
            qty+=i.quantity
        for i in l:
            if i.name not in l_unique:
                l_unique.append(i.name)
        return render(request, 'mf_sell.html',context={"l":l_unique,"name":name,"price":price*qty})

@login_required(login_url='/account/login/')
def mf_single(request,name):
    user=request.user
    if MF.objects.filter(user=user,name=name,sold=True).exists():
        l=MF.objects.filter(user=user,name=name).order_by('last_date')
        l=l[:len(l)-1]
    else:
        l=MF.objects.filter(user=user,name=name).order_by('last_date')
    x=0
    q=0
    for j in l:
        x+=j.amount*j.quantity
        q+=j.quantity
    try:
        dict=[q,x/q,l[0].last_date,name,l[0].is_sip]
    except:
        dict=[]
    return render(request, 'mf_single.html',context={"dict":dict,'l':l,'name':name})

@login_required(login_url='/account/login/')
def sold_prev(request):
    user=request.user
    l=MF.objects.filter(user=user,sold=True).order_by('last_date')
    lis=[]
    for i in l:
        if i.name not in lis:
            lis.append(i.name)
    this_year_invest=0
    dict={}
    for i in lis:
        a=MF.objects.filter(user=user,sold=True,name=i,last_date__year=datetime.now().year).order_by('-last_date','-id')[0]
        ama=a.amount*a.quantity
        this_year_invest+=ama
        obb=MF.objects.filter(user=user,sold=True,name=i)
        x=0
        q=0
        till=len(obb)-1
        for j in obb :
            if till==0:
                break
            x+=j.amount*j.quantity
            q+=j.quantity
            till-=1

        dict[i]=[a.quantity,a.amount,a.last_date,i,x,x/q,ama-x]
    return render(request, 'sold_prev.html',context={"l":l,"lis":lis,"this_year_invest":this_year_invest,'dict':dict})

@login_required(login_url='/account/login/')
def mf_home(request):
    user=request.user
    this_year_invest=Investment.objects.get(user=user,year=datetime.now().year).MF_i
    mf=MF.objects.filter(user=user,sold=False)
    l_unsold=[]
    for i in mf:
        l_unsold.append(i)
    l_unique=[]
    for i in l_unsold:
        if i.name not in l_unique:
            l_unique.append(i.name)
    dict={}
    total_portfolio=0
    for i in l_unique:
        l=MF.objects.filter(user=user,name=i,sold=False)
        l.order_by('last_date')
        x=0
        q=0
        for j in l:
            x+=j.amount*j.quantity
            q+=j.quantity
        dict[i]=[q,x/q,l[0].last_date,i,l[0].is_sip,l[len(l)-1].next_date,i]
        
        total_portfolio+=x
    return render(request, 'mf_home.html',context={"dict":dict,"total":total_portfolio,"this_year_invest":this_year_invest})


@login_required(login_url='/account/login/')
def mf_transact(request):
    if request.method=='POST':
        name=request.POST.get('name')
        amount=float(request.POST.get('amount'))
        date_bought=request.POST.get('date_bought')
        quantity=int(request.POST.get('quantity'))
        date_next=datetime.strptime(date_bought,"%Y-%m-%d")+timedelta(days=30)
        is_sip=request.POST.get('is_sip')
        print(name,amount,date_bought,quantity,is_sip)
        if not is_sip:
            is_sip=False
        if is_sip is False:
            date_next=None
            MF.objects.create(user=request.user,name=name,amount=amount,last_date=date_bought,is_sip=is_sip)
        else:
            MF.objects.create(user=request.user,name=name,amount=amount,last_date=date_bought,next_date=date_next,is_sip=is_sip)
        user=request.user
        balance=Balance.objects.get(user=user)
        balance.balance-=decimal.Decimal(amount)*decimal.Decimal(quantity)
        invest_obj=Investment.objects.get(user=user,year=datetime.now().year)
        invest_obj.invested_this_year+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        invest_obj.MF_i+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        balance.save()
        invest_obj.save()
        return redirect('mf_home')
    else:
        dict={}
        with open('codes.json') as file:
            dict=json.load(file)
        dict2={key: value for d in dict for value, key in d.items()}
        name=''
        price=0
        try:
            name=request.GET.get('name')
            price=decimal.Decimal(yf.download(str(dict2.get(name))+".BO",period='1d')['Close'].iloc[0])
        except:
            price=''
        return render(request, 'mf_buy.html',context={'name':name,'d':dict2,'price':price})
    
    
@login_required(login_url='/account/login/')
def mf_recomm(request):
    l=MFData.objects.filter(choice='l').order_by('rank')
    m=MFData.objects.filter(choice='m').order_by('rank')
    s=MFData.objects.filter(choice='s').order_by('rank')
    return render(request, 'mf_recomm.html',context={"l":l,"m":m,"s":s})


@login_required(login_url='/account/login/')
def investment_summary(request):
    inv_obj=Investment.objects.get(user=request.user,year=datetime.now().year)
    mf={'Name':'Mutual Funds','Amount':inv_obj.MF,'Invested':inv_obj.MF_i}
    smallcase={'Name':'SmallCase','Amount':inv_obj.SmallCase,'Invested':inv_obj.SmallCase_i}
    trade={'Name':'Trade','Amount':inv_obj.trade,'Invested':inv_obj.trade_i}
    large={'Name':'Large Cap Equity','Amount':inv_obj.large,'Invested':inv_obj.large_i}
    mid={'Name':'Mid Cap Equity','Amount':inv_obj.mid,'Invested':inv_obj.mid_i}
    small={'Name':'Small Cap Equity','Amount':inv_obj.small,'Invested':inv_obj.small_i}
    FD={'Name':'Fixed Deposits','Amount':inv_obj.FD,'Invested':inv_obj.FD_i}
    SGB={'Name':'Sovereign Gold Bonds','Amount':inv_obj.SGB,'Invested':inv_obj.SGB_i}
    inv_obj=[mf,smallcase,trade,large,mid,small,FD,SGB]
    return render(request, 'investment_summary.html',context={"inv":inv_obj})


@login_required(login_url='/account/login/')
def previous_investment(request):
    ...


@login_required(login_url='/account/login/')
def mf_predict(request):
    dict={}
    with open('codes.json') as file:
        dict=json.load(file)
    dict2={key: value for d in dict for value, key in d.items()}
    x=request.GET.get('opt')
    res=None
    if x:
        symbol=dict2[x]
        a,b,c,d,e,mn,mx=prediction(symbol)
        price=''
        try:
            price=yf.download(str(symbol)+".BO",period='1d')['Close'].iloc[0]
            prev_return=yf.Ticker(str(symbol)+".BO").get_info().get('annualHoldingsTurnover')
        
        except:
            price='Data Unable to Fetch'
            prev_return='Data Unable to Fetch'
        res={'a':a,'b':b,'c':c,'d':d,'e':e,'mn':mn,'mx':mx,'price':price,'prev_return':prev_return}
    return render(request, 'mf_predict.html',context={"dict":dict2,"res":res,"x":x})