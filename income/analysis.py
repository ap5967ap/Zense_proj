from django.http import HttpResponse, JsonResponse
from .models import IncomeObject
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from django.db.models import Sum,Avg
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

@login_required(login_url='login/')
def analysis_single(request,source):
    inflation_dict=get_inflation().keys()
    user=request.user
    income=IncomeObject.objects.filter(user=user,source=source,added=True)
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
    for i in income_obj:
        last_year_income.append(i.amount)
    last=income.order_by('-last_date').first()
    first_year=income.order_by('last_date').first().last_date.year
    current_year=max(inflation_dict)
    income_all_years=[]
    for i in range(first_year,current_year+2):
        income_all_years.append(income_in_year(income,i))
    contribution_all_years=[]
    total_objs=IncomeObject.objects.filter(user=user,added=True)
    for i in range(first_year,current_year+2):
        contribution_all_years.append((income_in_year(income,i)/income_in_year(total_objs,i))*100)
    return JsonResponse({'last':last.last_date.strftime("%d %b %Y"),'contribution':contribution,'last_year_income':last_year_income,'income_all_years':income_all_years,'contribution_all_years':contribution_all_years})

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
