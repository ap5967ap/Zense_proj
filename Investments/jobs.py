import time
from .models import Investment
from schedule import Scheduler
import threading
from datetime import datetime
import time
from account.models import Account
from balance.models import Balance
def job():
    all_user=Account.objects.all()
    if datetime.now().month==1 and (datetime.now().day==1 or datetime.now().day==2 or datetime.now().day==3 or datetime.now().day==4 or datetime.now().day==5 or datetime.now().day==6 or datetime.now().day==7):
        for user in all_user:
            is_created=Investment.objects.filter(user=user,year=datetime.now().year).exists()
            if is_created:
                continue
            balance=Balance.objects.get(user=user)
            to_invest=balance.invest_p
            age=datetime.now().year-user.dob.year
            safe=age
            risky=100-safe
            MF=risky/100*to_invest*20/100
            SmallCase=risky/100*to_invest*15/100
            if age <50:
                trade=risky/100*to_invest*10/100
                large=risky/100*to_invest*33/100
                mid=risky/100*to_invest*14/100
                small=risky/100*to_invest*8/100
            else:
                trade=0
                large=risky/100*to_invest*40/100
                mid=risky/100*to_invest*15/100
                small=risky/100*to_invest*10/100
            FD=safe/100*to_invest*60/100
            SGB=safe/100*to_invest*40/100
            obj=Investment.objects.create(user=user,to_invest=to_invest,invested_this_year=0,year=datetime.now().year,
                                          done=True,
                                          risky=risky,
                                          safe=safe,
                                          MF=MF,
                                          SmallCase=SmallCase,
                                          trade=trade,
                                          large=large,
                                          mid=mid,
                                          small=small,
                                          FD=FD,
                                          SGB=SGB)
            obj.save()
            
        
def run_continuously(self, interval=86400):
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
    scheduler.every(86400).seconds.do(job)
    scheduler.run_continuously()
        