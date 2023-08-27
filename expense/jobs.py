import time
from .models import Expense,Wants,Needs
from schedule import Scheduler
from account.models import Account
import threading
from datetime import datetime, timedelta 
import time
from balance.models import Balance
from .views import _re
import decimal
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def one_month_ago():
    '''Returns the date one month ago'''
    return datetime.now()-timedelta(days=30)

def job(do=False):
    try:
        all_user=Account.objects.all()
        if do or (datetime.now().day in [2,3,4,5,6,7]):
            for user in all_user:
                is_created=Expense.objects.filter(user=user,date__month=datetime.now().month,date__year=datetime.now().year).exists()
                if is_created:
                    continue
                try:
                    balance=Balance.objects.get(user=user)
                except:
                    balance=Balance.objects.create(user=user)
                    balance.save()
                to_expense=balance.expense
                wants=to_expense*decimal.Decimal(0.60)
                needs=to_expense*decimal.Decimal(0.40)
                objprev=Expense.objects.get(user=user,date__month=one_month_ago().month,date__year=one_month_ago().year)
                left=max(0,objprev.wants)
                left2=max(0,objprev.needs)
                buffer2=left2+objprev.buffer2
                buffer=left+objprev.buffer
                obj=Expense.objects.create(user=user,to_expense=to_expense,wants=wants,needs=needs,date=datetime.now(),buffer=buffer,buffer2=buffer2,used_this_month=0)
                obj.save()
                
    except Exception as e:
        file=open('cron_log.log','a')
        file.write(str(e)+'\n')


    all_income_automatically=Wants.objects.filter(status=True,is_active=True)
    log=open("cron_log.log",'a')
    if all_income_automatically.exists():
        for user_income in all_income_automatically:
            if_added=Wants.objects.filter(source=user_income.source,last_date=datetime.now().date()).exists()
            if if_added:
                continue
            if user_income.next_date == datetime.now().date():
                balance=Balance.objects.get(user=user_income.user)
                err=''
                bal=Balance.objects.get(user=user_income.user)
                if bal.balance<decimal.Decimal(user_income.amount):
                    err='You do not have enough balance'
                    message=render_to_string('wants_mail.html',{'user':user_income.user,'income':user_income,'balance':balance,'err':err})
                    email=EmailMessage('Expense not debited',message,to=[user_income.user.email])
                    try :
                        email.send()
                    except:
                        log.write(f"Email not sent to {user.email} on {datetime.now()}\n")
                    continue
                
                amount=user_income.amount
                frequency=user_income.frequency
                user=user_income.user
                try:
                    x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
                except:
                    bal=Balance.objects.get(user=user)
                    to_expense=bal.expense
                    x=Expense.objects.create(user=user,date=datetime.now(),to_expense=to_expense,wants=to_expense*decimal.Decimal(0.60),needs=to_expense*decimal.Decimal(0.40),wants_i=0,needs_i=0,buffer=0,used_this_month=0)
                    x.save()
                if x.wants<decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0) and x.buffer >=decimal.Decimal(amount) :
                    x.buffer=x.buffer-decimal.Decimal(amount)
                    x.save()
                elif x.wants>decimal.Decimal(amount):
                    x.wants=x.wants-decimal.Decimal(amount)
                    x.save()
                elif (x.wants+x.buffer)>=decimal.Decimal(amount) and (_re(frequency)>=91 or _re(frequency)==0):
                    x.buffer=0
                    x.wants=x.wants-decimal.Decimal(amount)-x.buffer
                    x.save()     
                else:
                    err='Your budget is not allowing you to spend this much'
                    message=render_to_string('wants_mail.html',{'user':user_income.user,'income':user_income,'balance':balance,'err':err})
                    email=EmailMessage('Expense not debited',message,to=[user_income.user.email])
                    try :
                        email.send()
                    except:
                        log.write(f"Email not sent to {user.email} on {datetime.now()}\n")
                    continue
                x=Expense.objects.get(user=user,date__month=datetime.now().month,date__year=datetime.now().year)
                x.used_this_month=x.used_this_month+decimal.Decimal(amount)
                x.wants_i=x.wants_i+decimal.Decimal(amount)
                balance.save()  
                x.save()
                bal=Balance.objects.get(user=user)
                bal.balance=bal.balance-decimal.Decimal(amount)
                bal.save()
                user_income.user.save()
                new_income=Wants.objects.create(source=user_income.source, amount=user_income.amount, frequency=user_income.frequency, last_date=datetime.now().date(),
                                             status=user_income.status, next_date=datetime.now().date()+timedelta(_re(user_income.frequency)), user=user_income.user,
                                             is_active=user_income.is_active,
                                             category=user_income.category)
                new_income.save()   
                subject=f"Expense for {user_income.source} debited successfully"
                message=render_to_string('wants_mail.html',{'user':user,'income':user_income,'balance':balance})
                email=EmailMessage(subject,message,to=[user.email])
                try :
                    email.send()
                except:
                    log.write(f"Email not sent to {user.email} on {datetime.now()}\n")
 
    all_needs=Needs.objects.filter(is_active=True).order_by('priority')
    if all_needs.exists():
        for i in all_needs:
            if  (i.next_date == datetime.now().date() and i.is_active):
                if_added=Needs.objects.filter(source=i.source,last_date__month=datetime.now().month,last_date__year=datetime.now().year).exists()
                if if_added:
                    continue
                xx=i.amount
                y=i.amount_added
                z=i.price
                inv=Expense.objects.get(user=i.user,date__month=datetime.now().month,date__year=datetime.now().year)
                max_add=inv.needs
                to_add=min(xx,z-y)
                if to_add>max_add:
                    to_add=max_add
                if y>=z or to_add==0:
                    subject=f"Amount for {i.source} fully saved."
                    message=render_to_string('needs_mail.html',{'user':i.user,'needs':i,'err':False})
                    email=EmailMessage(subject,message,to=[i.user.email])
                    try :
                        email.send()
                    except:
                        log.write(f"Email not sent to {i.user.email} on {datetime.now()}\n")
                    continue
                bal=Balance.objects.get(user=i.user)
                if bal.balance<to_add:
                    subject=f"Amount for {i.source} not saved due to low balance."
                    message=render_to_string('needs_mail.html',{'user':i.user,'needs':i,'err':'You do not have enough balance'})
                    email=EmailMessage(subject,message,to=[i.user.email])
                    try :
                        email.send()
                    except:
                        log.write(f"Email not sent to {i.user.email} on {datetime.now()}\n")
                    continue
                bal=Balance.objects.get(user=i.user)
                x=Needs.objects.create(source=i.source,amount=to_add,amount_added=i.amount_added+to_add,price=i.price,last_date=datetime.now().date(),next_date=datetime.now().date()+timedelta(days=30),buy_date=i.buy_date,user=i.user,is_active=True,category=i.category,priority=i.priority) 
                x.save()
                inv.needs=inv.needs-to_add
                inv.needs_i=inv.needs_i+to_add
                inv.used_this_month=inv.used_this_month+to_add                   
                inv.save()
                bal.balance=bal.balance-to_add
                bal.save()
    all_done=Needs.objects.filter(buy_date=datetime.now().date())
    if all_done.exists():
        for i in all_done:
            if i.price <= i.amount_added:
                subject=f"Amount for {i.source} fully saved"
                message=render_to_string('needs_mail.html',{'user':i.user,'needs':i,'err':False})
                email=EmailMessage(subject,message,to=[i.user.email])
                try :
                    email.send()
                except:
                    log.write(f"Email not sent to {i.user.email} on {datetime.now()}\n")
                continue
            if i.price > i.amount_added:
                subject=f"Amount for {i.source} is not fully saved"
                message=render_to_string('needs_mail.html',{'user':i.user,'needs':i,'err':'You have not saved enough amount to buy this item.'})
                email=EmailMessage(subject,message,to=[i.user.email])
                try :
                    email.send()
                except:
                    log.write(f"Email not sent to {i.user.email} on {datetime.now()}\n")
                continue
                
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