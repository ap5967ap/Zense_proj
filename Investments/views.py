import decimal
import json
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
import requests
from .models import MF,Investment,MFData,StockData,Stock
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .mutual_fund_data import prediction
from balance.models import Balance
import yfinance as yf
from income.analysis import get_inflation
from django.db.models import Sum
from django.contrib import messages
from .stocks import rsi_,ns
from tradingview_ta import TA_Handler, Interval, Exchange
from expense.models import *


@login_required(login_url='/account/login/')
def stock_recomm(request):
    l=StockData.objects.filter(category='l',rating__gt=0,buysignal__gt = 0).order_by('-rating','-buysignal')
    m=StockData.objects.filter(category='m',rating__gt=0,buysignal__gt = 0).order_by('-rating','-buysignal')
    s=StockData.objects.filter(category='s',rating__gt=0,buysignal__gt = 0).order_by('-rating','-buysignal')
    return render(request, 'stock_recomm.html',context={"l":l,"m":m,"s":s})
    

@login_required(login_url='/account/login/')
def stock_predict(request):  
    name=request.GET.get('name')
    l=ns().keys()
    lis=[]
    for i in l:
        lis.append(i)
        
    if not name:
        symbol=''
    else:
        symbol=ns().get(name.upper())
    if name and StockData.objects.filter(symbol=symbol).exists() :
        if symbol is None:
            return HttpResponse('Invalid Stock Name')
        try:
            obj=StockData.objects.get(symbol=symbol)
            price=obj.price
            a=obj.week52low * decimal.Decimal(1.5) 
            b=obj.week52low * decimal.Decimal(1.3)
            c=obj.week52low * decimal.Decimal(1.1)
            d=obj.week52low * decimal.Decimal(0.9)
            e=obj.week52high * decimal.Decimal(1.25)
            f=obj.week52high * decimal.Decimal(0.75)
            messages.info(request,message="Fields with value 0 indicates that the data is not available")
            return render(request, 'stock_predict.html',context={"lis":lis,"name":name,"price":price,"o":obj,'a':a,'b':b,'c':c,'d':d,'e':e,'f':f})
        except Exception as e:
            return HttpResponse(e)
    else:
      try: 
        sym=ns().get(name.strip().upper())
        category='n'
        data=yf.Ticker(sym+'.NS').get_info()
        price=data.get('previousClose')
        if not price:price=0
        pe=data.get('trailingPE')
        if not pe:pe=0
        pb=data.get('priceToBook')
        if not pb:pb=0
        roe=data.get('returnOnEquity')
        if not roe:roe=0
        doe=data.get('debtToEquity')
        if not doe:doe=0
        enterpriseToEbitda=data.get('enterpriseToEbitda')
        if not enterpriseToEbitda:enterpriseToEbitda=0
        week52low=data.get('fiftyTwoWeekLow')
        if not week52low:week52low=0
        week52high=data.get('fiftyTwoWeekHigh')
        if not week52high:week52high=0
        dividendYield=data.get('dividendYield')
        if not dividendYield:dividendYield=0
        esg=0
        headers={
            'User-Agent':'Mozilla/5.0'
        }
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/sustainability?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        esg=100
        try:
            esg=int(soup.find(class_="Fz(36px) Fw(600) D(ib) Mend(5px)").text.strip())
        except:
            esg=100
        ma50=0
        ma200=0
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/key-statistics?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        try:
            ma50=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[14].text.strip().split(',')))
            ma200=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[15].text.strip().split(',')))
        except:
            pass
        rsi=rsi_(yf.download(sym+'.NS', period='max'))
        rsi=float(rsi.iloc[-1])
        ta='n'
        d={
            'BUY':'b',
            'SELL':'s',
            'NEUTRAL':'n',
            'STRONG_BUY':'sb',
            'STRONG_SELL':'ss',
        }
        
        handler = TA_Handler(
            symbol=sym,
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_MONTH,
        )
        ta2=handler.get_analysis().summary.get('RECOMMENDATION')
        analysis = d[ta2]
        rating=0
        tot=0
        tot+=5
        if pe<=10:
            rating+=5
        elif pe<=15:
            rating+=4
        elif pe<=26:
            rating+=3
        elif pe<32:
            rating+=2
        else:
            rating+=1
        tot+=5
        if pb<=1:
            rating+=5
        elif pb<=3:
            rating+=4
        elif pb<=5:
            rating+=3
        elif pb<9:
            rating+=2
        else:
            rating+=1
        tot+=5
        if roe>=20:
            rating+=5
        elif roe>=15:
            rating+=4
        elif roe>=10:
            rating+=3
        elif roe>5:
            rating+=2
        else:
            rating+=1
        if doe<=0.5:
            rating+=5
        elif doe<=1:
            rating+=4
        elif doe<=2:
            rating+=3
        elif doe<=3:
            rating+=2
        else:
            rating+=1
        tot+=5
        if enterpriseToEbitda<=10:
            rating+=5
        elif enterpriseToEbitda<=15:
            rating+=4
        elif enterpriseToEbitda<=20:
            rating+=3
        elif enterpriseToEbitda<=25:
            rating+=2
        else:
            rating+=1
        buysignal=0
        tot+=5
        if dividendYield>=5:
            rating+=5
        elif dividendYield>=4:
            rating+=4
        elif dividendYield>=2:
            rating+=3
        elif dividendYield>=1:
            rating+=2
        else:
            rating+=1
        tot+=5
        if esg ==100:
            tot-=5
        if esg <10:
            rating+=5
        elif esg<20:
            rating+=4
        elif esg<30:
            rating+=3
        elif esg<40:
            rating+=2
        else:
            if esg >99:
                rating+=0
            else:
                rating+=1
        rating=rating/tot*5
        tot=0
        tot+=5
        if price>=week52low*1.5:
            buysignal+=5
        elif price>=week52low*1.25:
            buysignal+=4
        elif price>=week52low*1.1:
            buysignal+=3
        elif price>=week52low*0.9:
            buysignal+=2
        else:
            buysignal+=1
        tot+=4
        if ma50>=ma200:
            buysignal+=4
        else:
            buysignal+=2
        if price > ma50:
            buysignal+=4
        else:
            buysignal+=2
        tot+=5
        if rsi<=30:
            buysignal+=5
        elif rsi<=40:
            buysignal+=4
        elif rsi<=60:
            buysignal+=3
        elif rsi<=70:
            buysignal+=2
        else:
            buysignal+=1
        tot+=15
        if analysis=='sb':
            buysignal+=15
        elif analysis=='b':
            buysignal+=10
        elif analysis=='n':
            buysignal+=5
        elif analysis=='s':
            buysignal-=1
        else:
            buysignal-=5
        buysignal=buysignal/tot*5
        obj=StockData.objects.create(name=name,symbol=sym,category=category,price=price,pe=pe,pb=pb,roe=roe,doe=doe,enterpriseToEbitda=enterpriseToEbitda,week52low=week52low,week52high=week52high,dividendYield=dividendYield,ESG=esg,ma50=ma50,ma200=ma200,rsi=rsi,ta=ta,rating=0,buysignal=0)
        obj.save()
        a=obj.week52low *1.5 
        b=obj.week52low * (1.3)
        c=obj.week52low * (1.1)
        d=obj.week52low * (0.9)
        e=obj.week52high * (1.25)
        f=obj.week52high * (0.75)
        messages.info(request,message="Fields with value 0 indicates that the data is not available")
        return render(request, 'stock_predict.html',context={"lis":lis,"name":name,"price":price,'a':a,'b':b,'c':c,'d':d,'e':e,'f':f,'o':obj,'l':0})
      except:
            lis=[]
            for i in ns().keys():
                lis.append(i)
            return render(request, 'stock_predict.html',context={"lis":lis,'no':1})#,context={"lis":lis,"name":name,"price":'','a':0,'b':0,'c':0,'d':0,'e':0,'f':0,'o':0,'l':1})



@login_required(login_url='/account/login/')
def stock_transact(request):
    if request.method=='POST':
        name=request.POST.get('name')
        symbol=ns().get(name.upper())
        quantity=int(request.POST.get('quantity'))
        amount=float(request.POST.get('amount'))
        date_bought=request.POST.get('date_bought')
        category=request.POST.get('category')
        Stock.objects.create(user=request.user,symbol=symbol,name=name,price=amount,date=date_bought,category=category,quantity=quantity)
        user=request.user
        balance=Balance.objects.get(user=user)
        balance.balance-=decimal.Decimal(amount)*decimal.Decimal(quantity)
        invest_obj=Investment.objects.get(user=user,year=datetime.now().year)
        invest_obj.invested_this_year+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        if category=='l':
            invest_obj.large_i+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        elif category=='m':
            invest_obj.mid_i+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        elif category=='s':
            invest_obj.small_i+=decimal.Decimal(amount)*decimal.Decimal(quantity)
        balance.save()
        invest_obj.save()
        return redirect('stock_home')
    else:
        l=ns().keys()
        lis=[]
        for i in l:
            lis.append(i)
        name=''
        try:
            name=request.GET.get('name')
            symbol=ns().get(name.upper())
        except:
            price=''
        return render(request, 'stock_transact.html',context={"lis":lis,"name":name,"price":''})

@login_required(login_url='/account/login/')
def stock_prev(request):
    user=request.user
    l=Investment.objects.filter(user=user).order_by('year')
    la=[]
    ma=[]
    sa=[]
    year=[]
    for i in l:
        la.append(float(i.large_i))
        ma.append(float(i.mid_i))
        sa.append(float(i.small_i))
        year.append(int(i.year))
    return JsonResponse(data={'la':la,'ma':ma,'sa':sa,'year':year})


@login_required(login_url='/account/login/')
def stock_home(request):
    user=request.user
    l_i=Investment.objects.get(user=user,year=datetime.now().year).large_i
    m_i=Investment.objects.get(user=user,year=datetime.now().year).mid_i
    s_i=Investment.objects.get(user=user,year=datetime.now().year).small_i
    this_year_invest=l_i+m_i+s_i
    l=Stock.objects.filter(user=user,is_active=True)
    l_unique=[]
    for i in l:
        if i.name not in l_unique:
            l_unique.append(i.name)
    dict={}
    total_portfolio=0
    for i in l_unique:
        l=Stock.objects.filter(user=user,name=i,is_active=True)
        l.order_by('date')
        x=0
        q=0
        for j in l:
            x+=j.price*j.quantity
            q+=j.quantity
        dict[i]=[q,x/q,l[len(l)-1].date,i,l[0].category]
        total_portfolio+=x
    return render(request, 'stock_home.html',context={"dict":dict,"total":total_portfolio,"this_year_invest":this_year_invest,'l_i':l_i,'m_i':m_i,'s_i':s_i})

def _yearly_average_buying_price(l):
    x=0
    q=0
    for i in l:
        x+=i.amount*i.quantity
        q+=i.quantity
    return x/q


def _yearly_average_buying_price2(l:list[Stock]):
    x=0
    q=0
    for i in l:
        if i.is_active:
            x+=i.price*i.quantity
        else:
            x+=i.sell_price*i.quantity
        q+=i.quantity
    return x/q

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
def stock_data_single(request,name):
    l=Stock.objects.filter(name=name,user=request.user).order_by('date')
    start_year=l[0].date.year
    end_year=datetime.now().year
    dict=[]
    for i in range(start_year,end_year+1):
        try:
            x=((_yearly_average_buying_price2(l.filter(date__year=i))-_yearly_average_buying_price2(l.filter(date__year=i-1)))/_yearly_average_buying_price2(l.filter(date__year=i-1))*100)
            dict.append(x)
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
def stock_single(request,name):
    user=request.user
    l=[]
    if Stock.objects.filter(user=user,name=name,is_active=True).exists():
        l=Stock.objects.filter(user=user,name=name,is_active=True).order_by('date')
    x=0
    q=0
    for j in l:
        x+=j.price*j.quantity
        q+=j.quantity
    dict=[]
    try:
        dict=[q,x/q,l[0].date,name,l[0].category]
    except:
        dict=[]
    closed=Stock.objects.filter(user=user,name=name,is_active=False).order_by('date')
    pl=[]
    mylist={}
    for i in closed:
        mylist[i.id]=[i.quantity,i.sell_price,i.date,i.sell_price*i.quantity-i.price]
    return render(request, 'stock_single.html',context={"dict":dict,'l':l,'name':name,'closed':closed,'pl':mylist})

@login_required(login_url='/account/login/')    
def stock_sell(request):
    user=request.user
    if request.method=='POST':
        name=request.POST.get('name')
        bought=Stock.objects.filter(user=user,is_active=True,name__iexact=name).exists()
        if not bought:
            messages.error(request,'You have not bought this Stock')
            return redirect('stock_home')
        quantity=int(request.POST.get('quantity'))
        a2=quantity
        amount=float(request.POST.get('amount'))#!per stock sell price
        date=request.POST.get('date')
        cho=request.POST.get('type')
        l=Stock.objects.filter(user=user,is_active=True,name=name).order_by('date')
        ll=l
        qty=0
        for i in l:
            qty+=i.quantity
        if qty<quantity:
            messages.error(request,'You have not bought this much quantity')
            return redirect('stock_sell')
        pro=0
        while quantity>0:
            if l[0].quantity>quantity:
                l[0].quantity-=quantity
                pro+=quantity*l[0].price
                l[0].save()
                quantity=0
            else:
                quantity-=l[0].quantity
                pro+=l[0].quantity*l[0].price
                l[0].delete()
                l=l[1:]
        obj=Stock.objects.create(user=user,symbol=ll[0].symbol,name=name,price=pro,date=date,category=l[0].category,quantity=a2,sell_price=amount,is_active=False)
        obj.save()
        bal=Balance.objects.get(user=user)
        bal.balance+=decimal.Decimal(amount)
        bal.save()
        if cho=='1':
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            inv.to_invest+=decimal.Decimal(amount)
            inv.save()
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
            inv=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
            inv.to_expense += decimal.Decimal(amount)
            inv.wants += decimal.Decimal(amount)*decimal.Decimal(0.60)
            inv.needs += decimal.Decimal(amount)*decimal.Decimal(0.40)
            inv.save()
            #* DONE: add to expense
        return redirect('stock_home')
    else:
        l=Stock.objects.filter(user=user,is_active=True)
        l_unique=[]
        dict2=ns()
        name=''
        try:
            name=request.GET.get('name')
        except:
            pass
        qty=0
        obb=Stock.objects.filter(user=user,name=name,is_active=True)
        for i in obb:
            qty+=i.quantity
        for i in l:
            if i.name not in l_unique:
                l_unique.append(i.name)
        return render(request, 'stock_sell.html',context={"l":l_unique,"name":name})

@login_required(login_url='/account/login/')
def stock_prev_sold(request):
    user=request.user
    l=Stock.objects.filter(user=user,is_active=False).order_by('date')
    lis=[]
    for i in l:
        if i.name not in lis:
            lis.append(i.name)
    this_year_invest=0
    dict={}
    #!price-told price of bought stock
    #!sell_price->price at which each stock was sold
    for i in lis:
        a=Stock.objects.filter(user=user,is_active=False,name__iexact=i,date__year=datetime.now().year).order_by('-date','-id')
        obb=Stock.objects.filter(user=user,is_active=False,name__iexact=i).order_by('-date','-id')
        if not obb:
            continue
        temp=0
        for i in a:
            temp+=i.quantity*i.sell_price
        this_year_invest+=temp
        x=0
        q=0
        pro=0
        avg=0
        name=obb[0].name
        for j in obb :
            x+=j.price
            q+=j.quantity
            avg+=j.sell_price*j.quantity
            pro+=j.price
        dict[i]=[q,avg/q,a[0].date,name,x,x/q,avg-x]
    return render(request, 'stock_prev.html',context={"l":l,"lis":lis,"this_year_invest":this_year_invest,'dict':dict})


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
        if cho=='1':
            inv=Investment.objects.get(user=user,year=datetime.now().year)
            inv.to_invest+=decimal.Decimal(amount)
            inv.save()
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
            inv=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
            inv.to_expense += decimal.Decimal(amount)
            inv.wants += decimal.Decimal(amount)*decimal.Decimal(0.60)
            inv.needs += decimal.Decimal(amount)*decimal.Decimal(0.40)
            inv.save()
        return redirect('mf_home')
        
    else:
        l=MF.objects.filter(user=user,sold=False)
        l_unique=[]
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
        if not is_sip:
            is_sip=False
        if is_sip is False:
            date_next=None
            MF.objects.create(user=request.user,name=name,amount=amount,last_date=date_bought,is_sip=is_sip,quantity=quantity)
        else:
            MF.objects.create(user=request.user,name=name,amount=amount,last_date=date_bought,next_date=date_next,is_sip=is_sip,quantity=quantity)
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
    year=request.GET.get('name')
    if not year:
        year=datetime.now().year
    try:
        inv_obj=Investment.objects.get(user=request.user,year=year)
        mf={'Name':'Mutual Funds','Amount':inv_obj.MF,'Invested':inv_obj.MF_i}
        smallcase={'Name':'SmallCase','Amount':inv_obj.SmallCase,'Invested':inv_obj.SmallCase_i}
        trade={'Name':'Trade','Amount':inv_obj.trade,'Invested':inv_obj.trade_i}
        large={'Name':'Large Cap Equity','Amount':inv_obj.large,'Invested':inv_obj.large_i}
        mid={'Name':'Mid Cap Equity','Amount':inv_obj.mid,'Invested':inv_obj.mid_i}
        small={'Name':'Small Cap Equity','Amount':inv_obj.small,'Invested':inv_obj.small_i}
        FD={'Name':'Fixed Deposits','Amount':inv_obj.FD,'Invested':inv_obj.FD_i}
        SGB={'Name':'Sovereign Gold Bonds','Amount':inv_obj.SGB,'Invested':inv_obj.SGB_i}
        inv_obj=[mf,smallcase,trade,large,mid,small,FD,SGB]
        return render(request, 'investment_summary.html',context={"inv":inv_obj,'year':year})
    except:
        return render(request, 'investment_summary.html',context={'year':year})




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