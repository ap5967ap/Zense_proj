import schedule 
import time
from manager.models import Manage
import random
from django.db.models import F
from schedule import Scheduler
import threading
from datetime import datetime
import time
def job():
    x=random.randint(1,10000)
    xx=Manage.objects.create(x=x)
    xx.save()
    print("I'm working...")
    log=open("cron_log.log","a")
    log.write(f"{datetime.now().date()} {datetime.now().time()}  Cron Job working...\n")

def run_continuously(self, interval=60000):
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
    scheduler.every(60000).seconds.do(job)
    scheduler.run_continuously()