import datetime
import decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import IncomeObject
from datetime import timedelta
import random
from balance.models import Balance
from .forms import IncomeAdd
from django.db.models import Sum
from .analysis import get_inflation
def _re(frequency: str):
    '''Returns the number of days after which the income will be repeated'''
    if frequency == 'Daily':
        return 1
    elif frequency == 'Weekly':
        return 7
    elif frequency == 'Monthly':
        return 30
    elif frequency == 'Yearly':
        return 365
    else:
        return 0


@login_required(login_url='/account/login/')
def add_income(request):
    '''Adds income to the database'''
    message = ''
    name=""
    try:
        name = request.GET.get('name')
    except:
        pass
    
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = decimal.Decimal(request.POST.get('amount'))
        frequency = str(request.POST.get('frequency'))
        last_date = datetime.datetime.strptime(request.POST.get('last_date'),'%Y-%m-%d').date()
        user = request.user
        description = request.POST.get('description')
        if timedelta(_re(frequency)) == 0:
            next_date = None
        else:
            next_date = last_date+timedelta(_re(frequency))
        status = request.POST.get('status')
        if not status:
            status = False
        income_object = IncomeObject.objects.create(source=source, amount=amount, frequency=frequency,
                                                    last_date=last_date, added=True,status=status, next_date=next_date, user=user, description=description)
        income_object.save()
        balance=Balance.objects.get(user=request.user)
        balance.balance=balance.balance+amount
        balance.save()
        message = 'Income added successfully'
        return redirect('view_income')
    lis=[]
    for i in IncomeObject.objects.filter(user=request.user):
        lis.append(i.source)
    l=[]
    for i in lis:
        if i not in l:
            l.append(i)
    return render(request, 'add_income.html', {'message': message,'l':l,'name':name})


@login_required(login_url='/account/login/')
def view_income(request):
    '''View income'''
    income = IncomeObject.objects.filter(
        user=request.user).order_by('-next_date')
    income1 = []
    income2 = []
    
    for i in income:
        if (i.source not in income2 or i.frequency == 'Once') and (i.is_active == True):
            income1.append(i)
            income2.append(i.source)
    income1.sort(key=lambda x: x.next_date)
    return render(request, 'view_income.html', {'income': income1})


@login_required(login_url='/account/login/')
def edit_income(request, id):
    income = ''
    '''Edit income'''
    if request.method == 'POST':
        income = get_object_or_404(IncomeObject, id=id)
        amount = request.POST['amount']
        frequency = request.POST['frequency']
        description = request.POST['description']
        status = request.POST.get('status')
        if status is None:
            status = False
        income.status = status
        if timedelta(_re(frequency)) == 0:
            next_date = None
        else:
            next_date = income.last_date+timedelta(_re(frequency))
        
        income.amount = amount
        income.frequency = frequency
        income.description = description
        income.next_date = next_date
        income.save()
        return redirect('view_income')
    else:
        income = get_object_or_404(IncomeObject, id=id)
    return render(request, 'edit_income.html', {'income': income})

@login_required(login_url='/account/login/')
def delete_income(request, id):
    '''Delete income'''
    income = get_object_or_404(IncomeObject, id=id)
    income.delete()
    return redirect('view_income')

@login_required(login_url='/account/login/')
def add_object_income(request, id):
    '''Adds current period income'''
    income = get_object_or_404(IncomeObject, id=id)
    new_income = IncomeObject.objects.create(source=income.source, amount=income.amount, frequency=income.frequency, last_date=datetime.date.today(),
                                             status=income.status, next_date=datetime.date.today()+timedelta(_re(income.frequency)), user=income.user, description=income.description,
                                             added=True)
    new_income.save()
    balance=Balance.objects.get(user=request.user)
    balance.balance=balance.balance+income.amount
    balance.save()
    if timedelta(_re(income.frequency)) == 0:
        new_income.next_date = None
    new_income.save()
    return redirect('view_income')

@login_required(login_url='/account/login/')
def delete_source_income(request, source):
    '''Delete income'''
    income = IncomeObject.objects.filter(next_date__gte = datetime.date.today(),source=source).all().delete()
    is_left=IncomeObject.objects.filter(source=source).exists()
    if is_left:
        for i in IncomeObject.objects.filter(source=source).all():
            i.is_active=False
            i.save()
    return redirect('view_income')


def income_in_year(income, year:int):
    '''Returns the income in a particular year'''
    a=0
    try:
        a= float(income.filter(last_date__year=year).aggregate(Sum('amount'))['amount__sum'])
    except:
        a=0
    return a

@login_required(login_url='/account/login/')
def income_summary(request):
    return render(request,'income_summary.html')


@login_required(login_url='/account/login/')    
def income_summary_data(request):
    user=request.user
    inflation_dict=get_inflation()
    one_year_ago = datetime.datetime.now() - timedelta(days=365)
    lis=IncomeObject.objects.filter(user=user,added=True,last_date__gt=one_year_ago)
    if not lis:
        # return JsonResponse(data={"error":"No data available"})
        lis=IncomeObject.objects.filter(user=user,added=True)
        if not lis:
            return JsonResponse(data={"error":"No data available"})
    l=[]
    l2=[]
    for i in lis:
        if i.source not in l2:
            l2.append(i.source)
            l.append(i)
    value=[]
    for i in l:
        x=float(lis.filter(source=i.source).aggregate(Sum('amount'))['amount__sum'])
        value.append(x)
    last=lis.order_by('-last_date').first()
    lis=IncomeObject.objects.filter(user=user,added=True)
    first_year=lis.order_by('last_date').first().last_date.year
    current_year=max(inflation_dict.keys())
    inc=[]
    growth=[]
    for i in range(first_year,current_year+2):
        inc.append(float(income_in_year(lis,i)))
        try:
            x=float(((income_in_year(lis,i)-income_in_year(lis,i-1))/income_in_year(lis,i-1))*100)
            growth.append(x)
        except:
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
        
        
        
    return JsonResponse(data={
        'value':value,
        'inc':inc,
        'growth':growth,
        'infla':infla,
        'labels':labels,
        'l2':l2
    })