import decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from .models import Expense,Wants,Needs
from datetime import datetime, timedelta
from balance.models import Balance
from django.contrib import messages
from income.analysis import get_inflation,income_in_year
from Investments.models import Investment
from django.db.models import Sum

def _re(frequency: str)->int:
    '''Returns the number of days after will be repeated'''
    if frequency == 'Daily':
        return 1
    elif frequency == 'Weekly':
        return 7
    elif frequency == 'Monthly':
        return 30
    elif frequency == 'Yearly':
        return 365
    elif frequency == 'Quaterly':
        return 91
    elif frequency == 'Biannually':
        return 182
    else:
        return 0
    
@login_required(login_url='/account/login/')
def add_needs(request):
    if request.method=='POST':
        source=request.POST.get('source')
        amount=decimal.Decimal(request.POST.get('amount'))
        last_date=datetime.strptime(request.POST.get('last_date'),"%Y-%m-%d")
        buy_date=datetime.strptime(request.POST.get('buy_date'),"%Y-%m-%d")
        priority=Needs.objects.filter(user=request.user,is_active=True,priority__gt=0).count()+1
        user=request.user
        category=request.POST.get('category')
        bal=Balance.objects.get(user=user)
        
        if (buy_date-last_date).days<=30:
            month=datetime.now().month
            year=datetime.now().year
            exp=Expense.objects.get(user=request.user,date__month=month,date__year=year)
            buffer=request.POST.get('buffer')
            if not buffer:
                buffer=False
            if buffer:
                buffer2=exp.buffer2
                if buffer2<decimal.Decimal(amount):
                    messages.error(request,'You do not have enough balance even in the buffer from previous months. Either increase buy date or withdraw from other needs')
                    return redirect('add_needs')
                else:
                    exp.buffer2=exp.buffer2-decimal.Decimal(amount)
                    exp.save()
            elif (exp.needs)<decimal.Decimal(amount):
                messages.error(request,'Your budget is not enough to buy this item. Either increase buy date or withdraw from other needs')
                return redirect('add_needs')
            
            bal=Balance.objects.get(user=user)
            if bal.balance<decimal.Decimal(amount):
                messages.error(request,'You do not have enough balance')
                return redirect('add_needs')
            obj=Needs.objects.create(source=source,amount=amount,amount_added=amount,last_date=last_date,buy_date=buy_date,user=user,category=category,priority=priority)
            obj.save()
            exp.needs_i=exp.needs_i+decimal.Decimal(amount)
            exp.needs=exp.needs-decimal.Decimal(amount)
            exp.save()
            bal.balance=bal.balance-decimal.Decimal(amount)
            bal.save()
            messages.success(request,'Added successfully')
            return redirect('needs_view')
        else:
            month=(buy_date-last_date).days//30
            exp=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
            per_month=decimal.Decimal(amount)/month
            if (exp.needs+exp.needs_i)<per_month:
                messages.error(request,'Your budget is not enough to buy this item. Increase buy date.')
                return redirect('add_needs')    
            if bal.balance<min(exp.needs,per_month):
                messages.error(request,'You do not have enough balance')
                return redirect('add_needs')
            obj=Needs.objects.create(source=source,amount=per_month,price=amount,amount_added=min(exp.needs,per_month),last_date=last_date,buy_date=buy_date,user=user,category=category,priority=priority,next_date=last_date+timedelta(30))   
            obj.save()
            x=obj.amount_added
            exp.used_this_month=exp.used_this_month+x
            exp.needs_i=exp.needs_i+x
            exp.needs=exp.needs-x
            exp.save()
            bal=Balance.objects.get(user=user)
            bal.balance=bal.balance-x
            bal.save()
            messages.success(request,'Added successfully')
            return redirect('needs_view')
    else:
        x=Wants.objects.filter(user=request.user)
        l=[]
        for i in x:
            if i.category not in l:
                l.append(i.category)
        y=Needs.objects.filter(user=request.user)
        exp=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
        
        for i in y:
            if i.category not in l:
                l.append(i.category)
        return render(request,'add_needs.html',{'l':l,'bu':exp.buffer2})
            

@login_required(login_url='/account/login/')
def single_needs(request,source):
    need=Needs.objects.filter(user=request.user,source=source).order_by('-last_date','-id')
    inv=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
    is_buy_date=datetime.now().date()>=need[0].buy_date
    xx=need[0].price-need[0].amount_added
    x=max(30,int(xx/(need[0].amount)*30))
    lis=[need[len(need)-1].amount_added]
    dict={}
    c=0
    for i in range(len(need)-2,-1,-1):
        lis.append(need[i].amount_added-need[i+1].amount_added)
    lis.reverse()
    for i in need:
        dict[i]=[i,lis[c]]
        c+=1
    return render(request,'single_needs.html',{'n':need[0],'nn':dict,'source':source,'inv':inv,'is_buy_date':is_buy_date,'xx':xx,'x':x})

@login_required(login_url='/account/login/')
def withdraw(request,id):
    bal=Balance.objects.get(user=request.user)
    need=Needs.objects.get(id=id)
    bal.balance+=need.amount_added-need.price
    bal.save()
    for i in Needs.objects.filter(user=request.user,source=need.source):
        i.is_active=False
        i.priority=0
        i.save()
    messages.success(request,'Withdrawn successfully')
    return redirect('needs_view')

@login_required(login_url='/account/login/')
def add_need_to_expense(request,id):
    need=Needs.objects.get(id=id)
    amount_added= decimal.Decimal(need.amount_added)
    inv=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
    inv.to_expense += amount_added
    inv.wants += amount_added*decimal.Decimal(0.60)
    inv.needs += amount_added*decimal.Decimal(0.40)
    inv.save()
    bal=Balance.objects.get(user=request.user)
    bal.balance=bal.balance+need.amount_added
    bal.save()
    for i in Needs.objects.filter(user=request.user,source=need.source):
        i.is_active=False
        i.priority=0
        i.save()
    messages.success(request,'Added successfully')
    return redirect('needs_view')


@login_required(login_url='/account/login/')
def use_to_fund_other(request):
    if request.method=='POST':
        amount=decimal.Decimal(request.POST.get('amount'))
        source=request.POST.get('source')
        dest=request.POST.get('dest')
        source_obj=dest_obj=None
        try:
            source_obj=Needs.objects.filter(source=source,user=request.user,is_active=True).order_by('-last_date').first()
            dest_obj=Needs.objects.filter(source=dest,user=request.user,is_active=True).order_by('-last_date').first()
        except:
            pass
        if source_obj and dest_obj:
            if amount > dest_obj.amount_added:
                messages.error(request,'You can not transfer more than the amount added')
                return redirect('use_to_fund_other')
            dest_obj.amount_added-=amount
            dest_obj.remarks=f'Gave money for {source_obj.source} on {datetime.now().date()}'
            dest_obj.save()
            source_obj.amount_added+=amount
            source_obj.remarks=f'Received money from {dest_obj.source} on {datetime.now().date()}'
            source_obj.save()
            messages.success(request,'Added successfully')
            return redirect('needs_view')
        else:
            messages.error(request,'An error occured')
            return redirect('use_to_fund_other')
    else:
        lis=Needs.objects.filter(user=request.user,is_active=True)
        l=[]
        l2=[]
        for i in lis:
            if i.source not in l:
                l.append(i.source)
                l2.append(i)
        id=request.GET.get('id')
        try:
            i=Needs.objects.get(id=id)
        except: 
            i=''
        return render(request,'use_to_fund_other.html',{'id':i,'l':l2})


@login_required(login_url='/account/login/')
def add_need_to_investment(request,id):
    need=Needs.objects.get(id=id)
    amount_added= decimal.Decimal(need.amount_added)
    bal=Balance.objects.get(user=request.user)
    bal.balance=bal.balance+need.amount_added
    bal.save()
    user=request.user
    inv=Investment.objects.get(user=request.user,year=datetime.now().year)
    inv.to_invest+=decimal.Decimal(amount_added)
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
    for i in Needs.objects.filter(user=request.user,source=need.source):
        i.is_active=False
        i.priority=0
        i.save()
    return redirect('needs_view')


@login_required(login_url='/account/login/')
def use_buffer(request,id):
    inv=Expense.objects.get(user=request.user,date__month=datetime.now().month,date__year=datetime.now().year)
    need=Needs.objects.get(id=id)
    x=need.price-need.amount_added
    if inv.buffer2 and datetime.now().date()>=need.buy_date and inv.buffer2>=(need.price-need.amount_added) and (need.price>need.amount_added):
        new_need=Needs.objects.create(source=need.source,amount=(need.price-need.amount_added),price=need.price,last_date=datetime.now().date(),buy_date=need.buy_date,user=request.user,category=need.category,priority=need.priority,next_date=need.next_date,amount_added=need.amount_added+x,remarks="Added money from buffer")
        new_need.save()
        inv.buffer2=inv.buffer2-x
        inv.needs_i=inv.needs_i+x
        inv.used_this_month=inv.used_this_month+x
        inv.save()
        bal=Balance.objects.get(user=request.user)
        bal.balance=bal.balance-x
        bal.save()
        messages.success(request,'Added successfully')
        return redirect(f'/expense/single_needs/{need.source}/')
    
    
@login_required(login_url='/account/login/')
def increase_buy_date(request,id):
    days=int(request.POST.get('days')*1.5)
    if request.method=='POST':
        need=Needs.objects.get(id=id)
        need.buy_date=datetime.strptime(request.POST.get('buy_date'),' %Y-%m-%d')
        need.save()
        messages.success(request,'Buy date extended successfully')
        return redirect(f'/expense/single_needs/{need.source}/')
    else:
        need=Needs.objects.get(id=id)
        more=need.price-need.amount_added
        new_date=need.buy_date+timedelta(days)
        return render(request,'increase_buy_date.html',{'need':need,'days':days,'more':more})

@login_required(login_url='/account/login/')
def needs_view(request):
    '''Duplicates filtered'''
    income = Needs.objects.filter(user=request.user,is_active=True).order_by('-last_date')
    income1 = []
    income2 = []
    for i in income:
        if (i.source not in income2):
            income1.append(i)
            income2.append(i.source)
    income1.sort(key=lambda x: x.priority)
    
    income3 = Needs.objects.filter(user=request.user,is_active=False).order_by('-last_date')
    income4 = []
    income5 = []
    for i in income3:
        if (i.source not in income5):
            income4.append(i)
            income5.append(i.source)
    income4.sort(key=lambda x: x.priority)
    return render(request,'needs_view.html',{'lis':income1,'lis2':income4})
                  
@login_required(login_url='/account/login/')
def analysis_single_wants(request,source):
    lis=Wants.objects.filter(user=request.user,source=source)
    inflation_dict=get_inflation()
    user=request.user
    income=Wants.objects.filter(user=user,source__iexact=source)
    one_year_ago = datetime.now() - timedelta(days=365)
    total_obj=Wants.objects.filter(user=user,last_date__gte=one_year_ago,last_date__lte=datetime.now())
    total_income=0
    for i in total_obj:
        total_income+=i.amount
    income_obj=Wants.objects.filter(user=user,source=source,last_date__gte=one_year_ago,last_date__lte=datetime.now())
    income_contribution=0
    for i in income_obj:
        income_contribution+=i.amount
    try:
        contribution=(income_contribution/total_income)*100 #income contribution in percentage
    except ZeroDivisionError:
        contribution=0
    last_year_income=[]
    last_year_timings=[]
    for i in income_obj:
        last_year_income.append(float(i.amount))
        last_year_timings.append(i.last_date.strftime("%d-%m-%Y"))
    last=income.order_by('-last_date').first()
    first_year=income.order_by('last_date').first().last_date.year
    current_year=max(inflation_dict.keys())
    income_all_years=[]
    for i in range(first_year,current_year+2):
        income_all_years.append(int(income_in_year(income,i)))
    contribution_all_years=[]
    total_objs=Wants.objects.filter(user=user)
    for i in range(first_year,current_year+2):
        contribution_all_years.append(float((income_in_year(income,i)/income_in_year(total_objs,i))*100))
    growth=[]
    for i in range(first_year,current_year+2):
        try:
            x=float(((income_in_year(income,i)-income_in_year(income,i-1))/income_in_year(income,i-1))*100)
            growth.append(x)
        except ZeroDivisionError:
            growth.append(0)
    infla=[]
    labels=[]
    co=0
    for i in range(first_year,current_year+2):
        labels.append(i)
        try:
            infla.append(float(inflation_dict[i]))
        except KeyError:
            try:
                infla.append(infla[co-1])
            except:
                infla.append(0)
        co+=1
    contri_label=[source.capitalize(),'Rest of the Wants']
    my=Wants.objects.filter(user=user,source=source).order_by('-last_date')
    
    return render(request,'single_extra_detail.html',context=
                  {
                            'last_year_timings':last_year_timings[::-1],
                              'year':datetime.today().year,
                              'contri_label':contri_label,
                              'last':last.last_date.strftime("%d-%m-%Y"),
                              'contribution':int(contribution),
                              'last_year_income':last_year_income[::-1],
                              'income_all_years':income_all_years,
                              'contribution_all_years':contribution_all_years,
                              'growth':growth,
                              'inflation':infla,
                              'first_year':first_year,
                              'labels':labels,
                              'source':source,
                              'lis':lis,
                              'source':source,
                              'my':my,
                              
                  })

@login_required(login_url='/account/login/')
def analysis_single_wants_data(request,source):
    inflation_dict=get_inflation()
    user=request.user
    income=Wants.objects.filter(user=user,source__iexact=source)
    one_year_ago = datetime.now().date() - timedelta(days=365)
    total_obj=Wants.objects.filter(user=user,last_date__gte=one_year_ago,last_date__lte=datetime.now().date())
    total_income=0
    for i in total_obj:
        total_income+=i.amount
    income_obj=Wants.objects.filter(user=user,source=source,last_date__gte=one_year_ago,last_date__lte=datetime.now())
    income_contribution=0
    for i in income_obj:
        income_contribution+=i.amount
    try:
        contribution=(income_contribution/total_income)*100 #?income contribution in percentage
    except ZeroDivisionError:
        contribution=0
    last_year_income=[]
    last_year_timings=[]
    for i in income_obj:
        last_year_income.append(float(i.amount))
        last_year_timings.append(i.last_date.strftime("%d-%m-%Y"))
    last=income.order_by('-last_date').first()
    first_year=income.order_by('last_date').first().last_date.year
    current_year=max(inflation_dict.keys())
    income_all_years=[]
    for i in range(first_year,current_year+2):
        income_all_years.append(int(income_in_year(income,i)))
    contribution_all_years=[]
    total_objs=Wants.objects.filter(user=user)
    for i in range(first_year,current_year+2):
        contribution_all_years.append(float((income_in_year(income,i)/income_in_year(total_objs,i))*100))
    growth=[]
    for i in range(first_year,current_year+2):
        try:
            x=float(((income_in_year(income,i)-income_in_year(income,i-1))/income_in_year(income,i-1))*100)
            growth.append(x)
        except ZeroDivisionError:
            growth.append(0)
    infla=[]
    labels=[]
    co=0
    for i in range(first_year,current_year+2):
        labels.append(i)
        try:
            infla.append(float(inflation_dict[i]))
        except KeyError:
            try:
                infla.append(infla[co-1])
            except:
                infla.append(0)
        co+=1
    contri_label=[source.capitalize(),'Rest of the wants']
    return JsonResponse(data={
                              'last_year_timings':last_year_timings[::-1],
                              'year':datetime.today().year,
                              'contri_label':contri_label,
                              'last':last.last_date.strftime("%d-%m-%Y"),
                              'contribution':int(contribution),
                              'last_year_income':last_year_income[::-1],
                              'income_all_years':income_all_years,
                              'contribution_all_years':contribution_all_years,
                              'growth':growth,
                              'inflation':infla,
                              'first_year':first_year,
                              'labels':labels,
                              "source":source,
                              })

@login_required(login_url='/account/login/')
def add_wants(request):
    '''Adds expense to the database'''
    if request.method=='POST':
        source=request.POST.get('source')
        amount=decimal.Decimal(request.POST.get('amount'))
        frequency=request.POST.get('frequency')
        last_date=request.POST.get('last_date')
        user=request.user
        bal=Balance.objects.get(user=user)
        is_emergency=request.POST.get('is_emergency')
        if not is_emergency:
            is_emergency=False
        bal=Balance.objects.get(user=user)
        if bal.balance<decimal.Decimal(amount):
            messages.error(request,'You do not have enough balance')
            return redirect('add_wants')
        if is_emergency:
            pass
        else:
            try:
                x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
            except:
                bal=Balance.objects.get(user=user)
                to_expense=bal.expense
                x=Expense.objects.create(user=user,date=datetime.now(),to_expense=to_expense,wants=to_expense*decimal.Decimal(0.60),needs=to_expense*decimal.Decimal(0.40),wants_i=0,needs_i=0,buffer=0,used_this_month=0)
                x.save()
            if x.wants<decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0) and x.buffer >=decimal.Decimal(amount) :
                x.buffer=x.buffer-decimal.Decimal(amount)
                x.save()
            elif x.wants>decimal.Decimal(amount):
                x.wants=x.wants-decimal.Decimal(amount)
                x.save()
            elif (x.wants+x.buffer)>=decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0):
                x.buffer=0
                x.wants=x.wants-decimal.Decimal(amount)-x.buffer
                x.save()         
            else:
                messages.error(request,'You are not allowed to spend more this as it effects budget')
                return redirect('add_wants')       
        x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
        x.used_this_month=x.used_this_month+decimal.Decimal(amount)
        x.wants_i=x.wants_i+decimal.Decimal(amount)
        category=request.POST.get('category')
        x.save()         
        if _re(frequency)==0:
            obj=Wants.objects.create(source=source,amount=amount,frequency=frequency,last_date=last_date,user=user,status=False,category=category)
            obj.save()
        else:
            next_date=datetime.strptime(last_date,"%Y-%m-%d")+timedelta(_re(frequency))
            status=request.POST.get('status')
            if not status:
                status=False
            obj=Wants.objects.create(source=source,amount=amount,frequency=frequency,last_date=last_date,status=status,is_active=True,next_date=next_date,user=user,category=category)
            obj.save()
        messages.success(request,'Added successfully')
        bal=Balance.objects.get(user=user)
        bal.balance=bal.balance-decimal.Decimal(amount)
        bal.save()
        return redirect('view_wants')
    else:
        lis=Wants.objects.filter(user=request.user)
        source=''
        amount=''
        category=''
        lis=Wants.objects.filter(user=request.user).order_by('-last_date')
        lis2=[]
        for i in lis:
            if i.category not in lis2:
                lis2.append(i.category)
        try:
            source=request.GET.get('name')
            if source:
                amount=Wants.objects.filter(user=request.user,source__iexact=source).order_by('-last_date')[0].amount
                category=Wants.objects.filter(user=request.user,source__iexact=source).order_by('-last_date')[0].category
        except:...  
        l=[]
        for i in lis:
            if i.source not in l:
                l.append(i.source)
    return render(request,'add_wants.html',{'l':l,'source':source,'amount':amount,'cat':lis2,'cc':category})



@login_required(login_url='/account/login/')
def view_wants(request):
    '''View income'''
    income = Wants.objects.filter(
        user=request.user).order_by('-next_date')
    income1 = []
    income2 = []
    for i in income:
        if (i.source not in income2 or i.frequency == 'Once'):
            income1.append(i)
            income2.append(i.source)
    # income1.sort(key=lambda x: x.next_date)
    return render(request, 'view_wants.html', {'income': income1})


@login_required(login_url='/account/login/')
def edit_wants(request, id):
    income = ''
    '''Edit income'''
    if request.method == 'POST':
        income = get_object_or_404(Wants, id=id)
        amount = request.POST['amount']
        frequency = request.POST['frequency']
        status = request.POST.get('status')
        if not status :
            status = False
        income.status = status
        if timedelta(_re(frequency)) == 0:
            next_date = None
        else:
            next_date = income.last_date+timedelta(_re(frequency))
        x=income.amount
        income.amount = amount
        income.frequency = frequency
        income.next_date = next_date
        income.save()
        bal=Balance.objects.get(user=request.user)
        bal.balance=bal.balance+decimal.Decimal(x)-decimal.Decimal(amount)
        bal.save()
        return redirect('view_wants')
    else:
        income = get_object_or_404(Wants, id=id)
    return render(request, 'edit_wants.html', {'income': income})

@login_required(login_url='/account/login/')
def delete_wants(request, id):
    '''Delete income'''
    income = get_object_or_404(Wants, id=id)
    x=income.source
    income.delete()
    if Wants.objects.filter(source=x).exists():
        return redirect(f'/expense/analyse_single_wants/{x}')
    else:
        return redirect('view_wants')

@login_required(login_url='/account/login/')
def add_object_wants(request, id):
    '''Adds current period income'''
    income = get_object_or_404(Wants, id=id)
    
    bal=Balance.objects.get(user=request.user)
    if bal.balance<decimal.Decimal(income.amount):
            messages.error(request,'You do not have enough balance')
            return redirect('view_wants')
    user=request.user  
    amount=income.amount
    frequency=income.frequency
    try:
        x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
    except:
        bal=Balance.objects.get(user=user)
        to_expense=bal.expense
        x=Expense.objects.create(user=user,date=datetime.now(),to_expense=to_expense,wants=to_expense*decimal.Decimal(0.60),needs=to_expense*decimal.Decimal(0.40),wants_i=0,needs_i=0,buffer=0,used_this_month=0)
        x.save()
    if x.wants<decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0) and x.buffer >=decimal.Decimal(amount) :
        x.buffer=x.buffer-decimal.Decimal(amount)
        x.save()
    elif x.wants>decimal.Decimal(amount):
        x.wants=x.wants-decimal.Decimal(amount)
        x.save()
    elif (x.wants+x.buffer)>=decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0):
        x.buffer=0
        x.wants=x.wants-decimal.Decimal(amount)-x.buffer
        x.save()         
    else:
        messages.error(request,'You are not allowed to spend more this as it effects budget')
        return redirect('add_wants')       
    x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
    x.used_this_month=x.used_this_month+decimal.Decimal(amount)
    x.wants_i=x.wants_i+decimal.Decimal(amount)
    x.save()
    bal=Balance.objects.get(user=user)
    bal.balance=bal.balance-decimal.Decimal(amount)
    bal.save()
    if income.frequency == 'Once':
        new_income = Wants.objects.create(source=income.source, amount=income.amount, frequency=income.frequency, last_date=datetime.date.today(),
                                      status=income.status, next_date=None, user=income.user,category=income.category)
        new_income.save()
    else:
        new_income = Wants.objects.create(source=income.source, amount=income.amount, frequency=income.frequency, last_date=datetime.date.today(),
                                             status=income.status, next_date=datetime.date.today()+timedelta(_re(income.frequency)), user=income.user,category=income.category)
        new_income.save()
    return redirect('view_wants')


@login_required(login_url='/account/login/')
def delete_source_wants(request, source):
    '''Delete income'''
    income = Wants.objects.filter(next_date__gt = datetime.now().date(),source=source).all().delete()
    is_left=Wants.objects.filter(source=source).exists()
    if is_left:
        for i in Wants.objects.filter(source=source).all():
            i.is_active=False
            i.save()
    return redirect('view_wants')


@login_required(login_url='/account/login/')
def change_priority(request):
    l=[]
    lis=[]
    obj=Needs.objects.filter(user=request.user,is_active=True)
    for i in obj:
        if i.source not in l:
            l.append(i.source)
            lis.append(i)
    if request.method=='POST':
        dict={}
        for i in request.POST:
            if i!='csrfmiddlewaretoken':
                dict[i]=request.POST.get(i)
                # x=Needs.objects.filter(user=request.user,source=i)
        x=list(dict.values())
        if len(x) != len(set(x)):
            messages.error(request,'Priority should be unique')
            return redirect('change_priority')
        for i in dict:
            obj2=Needs.objects.filter(user=request.user,source=i)
            for j in obj2:
                j.priority=dict[i]
                j.save()
        return redirect('needs_view')        
    else:
        return render(request,'change_priority.html',{'lis':lis,'c':len(lis)})
    
    
@login_required(login_url='/account/login/')
def expense_summary(request):
    lis=lis2=start=end=lis3=''
    d=''
    if request.method == 'POST':
        start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d")
        start=start-timedelta(1)
        end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d")
        lis=Wants.objects.filter(user=request.user,last_date__gte=start,last_date__lte=end).order_by('-last_date')
        lis2=[]
        for i in lis:
            if i.category not in lis2:
                lis2.append(i.category)
        lis3=[]
        for i in lis2:
            lis3.append(Wants.objects.filter(user=request.user,category=i,last_date__gte=start,last_date__lte=end).aggregate(Sum('amount'))['amount__sum'])
        d=dict(zip(lis2,lis3))
        start=(start+timedelta(1)).date()
        end=end.date()
    sl=[]
    g=ex=month=year=''
    try:
        g=Wants.objects.filter(user=request.user).order_by('-last_date').first().last_date
        for i in range(g.year,datetime.now().year+1):
            sl.append(i)
        month=datetime.now().month
        year=datetime.now().year
        try:    
            month=request.GET.get('month')
            year=request.GET.get('year')
        except:
            pass
        ex=''
        if not (month and year):
            month=datetime.now().month
            year=datetime.now().year
        if month and year:
            try:
                ex=Expense.objects.get(user=request.user,date__month=month,date__year=year)
            except:
                ex='85'

    except:...
    return render(request,'expense_summary.html',{'startd':start,'endd':end,'d':d,'lis':lis,'lis2':lis2,'start':g,'end':end,'lis3':lis3,'total':sum(lis3),'yr':sl,'ex':ex,'month':month,'year':year})
    
    
    
def category(request):
    start=end=lis=category=''
    if request.method == 'POST':
        start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d")
        start=start-timedelta(1)
        end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d")
        category=request.POST.get('category')
        lis=Wants.objects.filter(user=request.user,last_date__gte=start,last_date__lte=end,category__iexact=category).order_by('-last_date')
        start=(start+timedelta(1)).date()
        end=end.date()
    lis3=Wants.objects.filter(user=request.user).order_by('-last_date')
    lis2=[]
    for i in lis3:
        if i.category not in lis2:
            lis2.append(i.category)
    return render(request, 'single_category.html', {'lis': lis,'lis2':lis2,'start':start,'end':end,'category':category})
    