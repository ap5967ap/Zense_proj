import json
from django.core.mail import EmailMessage
import time
from .models import Investment,MF as MutualFund,Other,SGB as gold
from schedule import Scheduler
import threading
from datetime import datetime, timedelta
import time
from account.models import Account
from balance.models import Balance
import decimal
import yfinance as yf
from expense.models import Expense
from django.template.loader import render_to_string
def job(do=False):
    try:
       all_user=Account.objects.all()
       if do or (datetime.now().month==1 and (datetime.now().day==2 or datetime.now().day==3 or datetime.now().day==4 or datetime.now().day==5 or datetime.now().day==6 or datetime.now().day==7)):
         for user in all_user:
            is_created=Investment.objects.filter(user=user,year=datetime.now().year).exists()
            if is_created:
                continue
            try:
                balance=Balance.objects.get(user=user)
            except:
                Balance.objects.create(user=user)
                
            to_invest=balance.invest_p
            age=datetime.now().year-user.dob.year
            safe=age
            risky=100-safe
            MF=decimal.Decimal(risky/100)*to_invest*decimal.Decimal(35/100)
            large=decimal.Decimal(risky/100)*to_invest*decimal.Decimal(40/100)
            mid=decimal.Decimal(risky/100)*to_invest*decimal.Decimal(15/100)
            small=decimal.Decimal(risky/100)*to_invest*decimal.Decimal(10/100)
            FD=decimal.Decimal(safe/100)*to_invest*decimal.Decimal(60/100)
            SGB=decimal.Decimal(safe/100)*to_invest*decimal.Decimal(40/100)
            obj=Investment.objects.create(user=user,to_invest=to_invest,invested_this_year=0,year=datetime.now().year,
                                          done=True,
                                          risky=risky,
                                          safe=safe,
                                          MF=MF,
                                          large=large,
                                          mid=mid,
                                          small=small,
                                          FD=FD,
                                          SGB=SGB)
            obj.save()
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')
    if do:
        return
    try:#!MF sip is auto paid
        obj=MutualFund.objects.filter(is_sip=True,sold=False)
        dict={}
        with open('codes.json') as file:
            dict=json.load(file)
        dict2={key: value for d in dict for value, key in d.items()}
        for i in obj:
            if i.next_date==datetime.now().date():
                symbol=dict2[i.name]
                is_paid=MutualFund.objects.filter(user=i.user,name=i.name,last_date=i.next_date,sold=False).exists()
                try:
                    price=decimal.Decimal(yf.download(str(symbol)+".BO",period='1d')['Close'].iloc[0])
                except:
                    price=i.amount
                quantity=decimal.Decimal(i.quantity)
                if is_paid:
                    continue
                last_date=datetime.now().date()
                next_date=datetime.now().date()+timedelta(days=30)
                user=i.user
                balance=Balance.objects.get(user=user)
                d=decimal.Decimal(price)*decimal.Decimal(quantity)
                balance.balance-=decimal.Decimal(price)*decimal.Decimal(quantity)
                invest_obj=Investment.objects.get(user=user,year=datetime.now().year)
                invest_obj.invested_this_year+=d
                invest_obj.MF_i+=d
                balance.save()
                invest_obj.save()
                ob=MutualFund.objects.create(user=user,name=i.name,amount=price,quantity=quantity,last_date=last_date,next_date=next_date,is_sip=True,sold=False)
                ob.save()
                subject=f'Paid monthly sip of {i.amount} for {i.name}'
                message=render_to_string('sip_paid.html',{'user':user,'amount':i.amount,'name':i.name})
                email=EmailMessage(subject,message,to=[user.email])
                try:
                    email.send()
                except:
                    with open('cron_log.log','a') as file:
                        file.write(f"Email not sent to {user.email} on {datetime.now().date()} for SIP \n")
    except:
        with open('cron_log.log','a') as file:
            file.write(f"Error in MF SIP on {datetime.now().date()}\n")
    try:
        fd=Other.objects.filter(category='FD',is_active=True,sell_date=datetime.now().date())
        for i in fd:
            i.is_active=False
            i.save()
            bal=Balance.objects.get(user=i.user)
            bal.balance+=decimal.Decimal(i.sell_price)
            bal.save()
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
            message=render_to_string('fd_sold.html',{'user':user,'amount':i.price,'name':i.name,'s':i.sell_price})
            email=EmailMessage(subject,message,to=[user.email])
            try:
                email.send()
            except:
                with open('cron_log.log','a') as file:
                    file.write(f"Email not sent to {user.email} on {datetime.now().date()} for SIP \n")
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')  

    try:
        lis=gold.objects.filter(is_active=True,sell_date__gte=datetime.now().date())
        for i in lis:
            user=i.user
            subject=f'SGB {i.price} {i.date} matured'
            email=EmailMessage(subject,f'SGB {i.price} {i.date} matured. Login into your account to sell it.',to=[user.email])
            try:
                email.send()
            except:
                with open('cron_log.log','a') as file:
                    file.write(f"Email not sent to {user.email} on {datetime.now().date()} for SIP \n")
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')
    
    try:
        lis=gold.objects.filter(is_active=True,sell_date__lt=datetime.now().date())
        for i in lis:
            if (datetime.now().date-i.date).days in [365,365*2,365*3,365*4,365*5,365*6,365*7,365*8,365*9,365*10,365*11]:
                bal=Balance.objects.get(user=i.user)
                bal.balance+=decimal.Decimal(i.price*2.5/100)
                bal.save()
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')

def run_continuously(self, interval=40000):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run

Scheduler.run_continuously = run_continuously

def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(40000).seconds.do(job)
    scheduler.run_continuously()
        