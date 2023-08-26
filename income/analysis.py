from django.http import JsonResponse
from django.shortcuts import render
from .models import IncomeObject
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from django.db.models import Sum



INFLATION_DATA_LINK="https://www.macrotrends.net/countries/IND/india/inflation-rate-cpi"
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

def income_in_year(income, year):
    '''Returns the income in a particular year'''
    a=0
    try:
        a= float(income.filter(last_date__year=year).aggregate(Sum('amount'))['amount__sum'])
    except:
        a=0
    return a


@login_required(login_url='/accounts/login/')
def analysis_single(request,id):
    source=IncomeObject.objects.get(id=id).source
    inflation_dict=get_inflation()
    user=request.user
    income=IncomeObject.objects.filter(user=user,source__iexact=source,added=True)
    one_year_ago = datetime.now() - timedelta(days=365)
    total_obj=IncomeObject.objects.filter(user=user,last_date__gte=one_year_ago,last_date__lte=datetime.now(),added=True)
    total_income=0
    for i in total_obj:
        total_income+=i.amount
    income_obj=IncomeObject.objects.filter(user=user,source=source,last_date__gte=one_year_ago,last_date__lte=datetime.now(),added=True)
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
    total_objs=IncomeObject.objects.filter(user=user,added=True)
    for i in range(first_year,current_year+2):
        try:
            contribution_all_years.append(float((income_in_year(income,i)/income_in_year(total_objs,i))*100))
        except ZeroDivisionError:
            contribution_all_years.append(0)
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
    contri_label=[source.capitalize(),'Rest of the income']
    my=IncomeObject.objects.filter(user=user,added=True,source=source).order_by('-last_date')
    return render(request,'single_income_detail.html',context=
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
                              'source':id,
                              'so':source,
                              'my':my,
                              
                  })



def get_inflation():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(INFLATION_DATA_LINK,headers=hdr)
    page=urlopen(req)
    soup= BeautifulSoup(page,features="html.parser")
    data={}
    table=soup.find_all('table', class_="historical_data_table table table-striped table-bordered")[1]
    for i in table.find_all('tr')[2:]:
        c=i.find_all('td')
        data[int(c[0].text.strip())]=float(c[1].text.strip()[:-1])
    return data



@login_required(login_url='/accounts/login/')
def single_analysis(request,source):
    '''used this function as we need to pass the (serialised) data in json format to the template'''
    source=IncomeObject.objects.get(id=source).source
    inflation_dict=get_inflation()
    user=request.user
    income=IncomeObject.objects.filter(user=user,source__iexact=source,added=True)
    one_year_ago = datetime.now() - timedelta(days=365)
    total_obj=IncomeObject.objects.filter(user=user,last_date__gte=one_year_ago,last_date__lte=datetime.now(),added=True)
    total_income=0
    for i in total_obj:
        total_income+=i.amount
    income_obj=IncomeObject.objects.filter(user=user,source=source,last_date__gte=one_year_ago,last_date__lte=datetime.now(),added=True)
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
    total_objs=IncomeObject.objects.filter(user=user,added=True)
    for i in range(first_year,current_year+2):
        try:
            contribution_all_years.append(float((income_in_year(income,i)/income_in_year(total_objs,i))*100))
        except ZeroDivisionError:
            contribution_all_years.append(0)
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
    contri_label=[source.capitalize(),'Rest of the income']
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
                              })