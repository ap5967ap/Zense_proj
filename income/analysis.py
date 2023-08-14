from django.http import JsonResponse
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
    return float(income.objects.filter(last_date__year=year).aggregate(Sum('amount'))['amount__sum'])

@login_required(login_url='login/')
def analysis_single(request,pk):
    user=request.user
    income=IncomeObject.objects.filter(user=user,pk=pk)
    one_year_ago = datetime.now() - timedelta(days=365)
    total_obj=IncomeObject.objects.filter(user=user,last_date__gte=one_year_ago,last_date__lte=datetime.now())
    total_income=0
    for i in total_obj:
        total_income+=i.amount
    income_obj=IncomeObject.objects.filter(user=user,pk=pk,last_date__gte=one_year_ago,last_date__lte=datetime.now())
    income_contribution=0
    for i in income_obj:
        income_contribution+=i.amount
    contribution=(income_contribution/total_income)*100 #income contribution in percentage
    last_year_income=[]
    for i in income_obj:
        last_year_income.append(i.amount)
    last=income.order_by('-last_date').first()
    first_year=income.order_by('last_date').first().last_date.year
    
    
    


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
