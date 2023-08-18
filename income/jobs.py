import time
from .models import IncomeObject
from balance.models import Balance
from schedule import Scheduler
import threading
import datetime
from datetime import timedelta
import time
from .views import _re
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def job():
    all_income_automatically=IncomeObject.objects.filter(status=True,is_active=True)
    log=open("cron_log.log",'a')
    if all_income_automatically.exists():
        for user_income in all_income_automatically:
            if_added=IncomeObject.objects.filter(source=user_income.source,last_date=datetime.date.today()).exists()
            if if_added:
                continue
            if user_income.next_date == datetime.date.today():
                user_income.added=True
                user_income.save()
                balance=Balance.objects.get(user=user_income.user)
                balance.balance=balance.balance+user_income.amount
                balance.save()  
                user_income.user.save()
                new_income=IncomeObject.objects.create(source=user_income.source, amount=user_income.amount, frequency=user_income.frequency, last_date=datetime.date.today(),
                                             status=user_income.status, next_date=datetime.date.today()+timedelta(_re(user_income.frequency)), user=user_income.user, description=user_income.description,
                                             added=True,is_active=user_income.is_active)
                user=user_income.user
                new_income.save()   
                subject=f"Income from {user_income.source} credited successfully"
                message=render_to_string('income_added_successfully.html',{'user':user,'income':user_income,'balance':balance})
                email=EmailMessage(subject,message,to=[user.email])
                try :
                    email.send()
                except:
                    log.write(f"Email not sent to {user.email} on {datetime.datetime.now()}\n")
                    
def run_continuously(self, interval=10):
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
    scheduler.every(10).seconds.do(job) #!running backend cron twice a day
    scheduler.run_continuously()