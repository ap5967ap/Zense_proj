import time
from .models import Balance
from income.models import IncomeObject
from schedule import Scheduler
import threading
from datetime import datetime 
import datetime as Datetime
import time
import decimal
def last_date():
    year=datetime.now().year
    month=datetime.now().month
    if month == 1:
        return Datetime.date(year-1,12,1)
    else:
        return Datetime.date(year,month-1,1)
    
def last_last_end():
    year=datetime.now().year
    month=datetime.now().month
    if month == 1:
        return Datetime.date(year-1,12,31)
    else:
        if month==3 or month==5 or month==7 or month==8 or month==10 or month==12:
            return Datetime.date(year,month-1,31)
        elif month==4 or month==6 or month==9 or month==11:
            return Datetime.date(year,month-1,30)
        elif month==2:
            if year%4==0:
                return Datetime.date(year,month-1,29)
            else:
                return Datetime.date(year,month-1,28)
def job():
    b=Balance.objects.all()
    if datetime.now().day==1 and b.exists() and datetime.now().month!=1:
        for i in b:
            if i.updated.month==datetime.now().month:
                continue
            user=i.user
            balance=Balance.objects.get(user=user)
            x=0
            income=IncomeObject.objects.filter(user=user,added=True,last_date__gte=last_date(),last_date__lte=last_last_end())
            for j in income:
                x+=j.amount
            balance.last_month=x
            balance.expense=x*decimal.Decimal(0.70)
            balance.invest+=x*decimal.Decimal(0.30)
            balance.invest_p=balance.invest
            balance.updated=datetime.now().date()
            balance.save()
    elif datetime.now().day==1 and b.exists() and datetime.now().month==1:
        for i in b:
            user=i.user
            balance=Balance.objects.get(user=user)
            x=0
            income=IncomeObject.objects.filter(user=user,added=True,last_date__gte=last_date(),last_date__lte=last_last_end())
            for j in income:
                x+=j.amount
            balance.last_month=x
            balance.expense=x*decimal.Decimal(0.70)
            balance.invest=x*decimal.Decimal(0.30)
            balance.updated=datetime.now().date()
            balance.save()
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