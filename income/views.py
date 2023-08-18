import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import IncomeObject
from datetime import timedelta
from balance.models import Balance
from bootstrap_datepicker_plus.widgets import DatePickerInput
from .forms import IncomeAdd
from .analysis import analysis_single, get_inflation


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
    form = IncomeAdd(request.POST or None)
    message = ''
    if request.method == 'POST' and form.is_valid():
        source = form.cleaned_data['source']
        amount = form.cleaned_data['amount']
        frequency = form.cleaned_data['frequency']
        last_date = form.cleaned_data['last_date']
        user = request.user
        description = form.cleaned_data['description']
        if timedelta(_re(frequency)) == 0:
            next_date = None
        else:
            next_date = last_date+timedelta(_re(frequency))
        status = form.cleaned_data.get('status')
        income_object = IncomeObject.objects.create(source=source, amount=amount, frequency=frequency,
                                                    last_date=last_date, added=True,status=status, next_date=next_date, user=user, description=description)
        income_object.save()
        balance=Balance.objects.get(user=request.user)
        balance.balance=balance.balance+amount
        balance.save()
        form = IncomeAdd()
        message = 'Income added successfully'
        return redirect('add_income')
    form = IncomeAdd()
    return render(request, 'add_income.html', {'message': message, 'form': form})


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