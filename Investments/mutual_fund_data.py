from .models import MFData
from bs4 import BeautifulSoup
import requests
import json
import math
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import yfinance as yf
import warnings
import time
from schedule import Scheduler
import threading
import time

warnings.simplefilter('ignore', ConvergenceWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARMA',FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA',FutureWarning)
def getDataFrame(scheme_code):
    def decorate(func):
        def decorated(*args,**kwargs):
            df = yf.download(str(scheme_code)+".BO",period='max')
            df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])
            df = df.rename(columns={'Close': 'nav'})
            df.reset_index(inplace=True)
            df['date'] = df['Date'].dt.strftime('%Y-%m-%d')

            info = yf.Ticker(str(scheme_code)+".BO").get_info()
            details = {'scheme_name': info['longName'], 'scheme_code': str(scheme_code)}
            return func(df,details)
        return decorated
    return decorate


def data_frame(func):
    def decorated(*args,**kwargs):
        df = yf.download(str(*args) + ".BO", period='max')
        df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])
        df = df.rename(columns={'Close': 'nav'})
        df.reset_index(inplace=True)
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        info = yf.Ticker(str(*args) + ".BO").get_info()
        details = {'scheme_name': info['longName'], 'scheme_code': str(*args)}
        return func(df,details)
    return decorated


def arima(df):
    days = 30
    df_new = df['nav'].astype(float)                                #.iloc[:-30] #exclude last day nav
    X = df_new.values
    size = int(len(X) * 0.90)
    train, test = X[0:size], X[size:len(X)]
    history = [x for x in train]
    prediction = list()
    for t in range(len(test)):
        model = ARIMA(history, order=(5, 1, 0))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        prediction.append(yhat)
        obs = test[t]
        history.append(obs)
    rmse = math.sqrt(mean_squared_error(test, prediction))
    history = [x for x in X]
    forecasting = []
    for i in range(days):
        model = ARIMA(history, order=(5, 1, 0))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        forecasting.append(yhat)    #future day
        history.append(yhat)
    return forecasting, rmse

def prediction(symbol):
    @getDataFrame(symbol)
    def forecasting_mutual_fund(df, details):
        x,y=arima(df)
        a=x[0]
        b=x[1]
        c=x[2]
        d=x[3]
        e=x[4]
        mn=min(x)
        mx=max(x)
        return (a,b,c,d,e,mn,mx)
    return forecasting_mutual_fund()    
def func(*args,**kwargs):
   try: 
    small="https://www.etmoney.com/mutual-funds/equity/small-cap/36"
    # MFData.objects.all().delete()
    r=requests.get(small)
    soup = BeautifulSoup(r.content, 'html5lib')
    name=""
    rank=""
    div=soup.find_all(class_="mfFund-block media")
    l=[]
    scheme_codes={}
    with open('codes.json') as f:
        scheme_codes=json.load(f)
    dict2={key: value for d in scheme_codes for value, key in d.items()}

    for i in div:
        try:
            name=i.find(class_='fund-name scheme-name').text.strip()+" "+"Direct Plan-Growth"
            rank=int(i.find(class_='etm-rank').find('strong', class_='item-value').text.strip()[1:])
            symbol=dict2[name]
            a,b,c,d,e,mn,mx=prediction(symbol)
            try:
                price=float(yf.download(str(symbol)+".BO",period='1d')['Close'].iloc[0])
                prev_return=yf.Ticker(str(symbol)+".BO").get_info().get('annualHoldingsTurnover')
            except:
                price=0
                prev_return=0
            obj=MFData.objects.create(name=name,rank=rank,choice='s',d1=a,d2=b,d3=c,d4=d,d5=e,dmin=mn,dmax=mx,price=price,prev_return=prev_return)
            obj.save()
        except:
            f=open("cron_log.log",'a')
            f.write(str(e)+'\n')
    mid="https://www.etmoney.com/mutual-funds/equity/mid-cap/35"
    r=requests.get(mid)
    soup=BeautifulSoup(r.content,'html5lib')
    div=soup.find_all(class_="mfFund-block media")
    for i in div:
        try:
            name=i.find(class_='fund-name scheme-name').text.strip()+" "+"Direct Plan-Growth"
            rank=int(i.find(class_='etm-rank').find('strong', class_='item-value').text.strip()[1:])
            symbol=dict2[name]
            a,b,c,d,e,mn,mx=prediction(symbol)
            try:
                price=float(yf.download(str(symbol)+".BO",period='1d')['Close'].iloc[0])
                prev_return=yf.Ticker(str(symbol)+".BO").get_info().get('annualHoldingsTurnover')
            except:
                price=0
                prev_return=0
            obj=MFData.objects.create(name=name,rank=rank,choice='m',d1=a,d2=b,d3=c,d4=d,d5=e,dmin=mn,dmax=mx,price=price,prev_return=prev_return)
            obj.save()
        except:
            f=open("cron_log.log",'a')
            f.write(str(e)+'\n')
    large="https://www.etmoney.com/mutual-funds/equity/large-cap/32"
    r=requests.get(large)
    soup=BeautifulSoup(r.content,'html5lib')
    div=soup.find_all(class_="mfFund-block media")
    for i in div:
        try:
            name=i.find(class_='fund-name scheme-name').text.strip()+" "+"Direct Plan-Growth"
            rank=int(i.find(class_='etm-rank').find('strong', class_='item-value').text.strip()[1:])
            symbol=dict2[name]
            a,b,c,d,e,mn,mx=prediction(symbol)
            try:
                price=float(yf.download(str(symbol)+".BO",period='1d')['Close'].iloc[0])
                prev_return=yf.Ticker(str(symbol)+".BO").get_info().get('annualHoldingsTurnover')
            except:
                price=0
                prev_return=0
            obj=MFData.objects.create(name=name,rank=rank,choice='l',d1=a,d2=b,d3=c,d4=d,d5=e,dmin=mn,dmax=mx,price=price,prev_return=prev_return)
            obj.save()
        except Exception as e:
            f=open("cron_log.log",'a')
            f.write(str(e)+'\n')
   except Exception as e:
       f=open("cron_log.log",'a')
       f.write(str(e)+'\n')
# func()
# def run_continuously(self, interval=86400):
#     """Continuously run, while executing pending jobs at each elapsed
#     time interval.
#     @return cease_continuous_run: threading.Event which can be set to
#     cease continuous run.
#     Please note that it is *intended behavior that run_continuously()
#     does not run missed jobs*. For example, if you've registered a job
#     that should run every minute and you set a continuous run interval
#     of one hour then your job won't be run 60 times at each interval but
#     only once.
#     """

#     cease_continuous_run = threading.Event()

#     class ScheduleThread(threading.Thread):

#         @classmethod
#         def run(cls):
#             while not cease_continuous_run.is_set():
#                 self.run_pending()
#                 time.sleep(interval)

#     continuous_thread = ScheduleThread()
#     continuous_thread.setDaemon(True)
#     continuous_thread.start()
#     return cease_continuous_run

# Scheduler.run_continuously = run_continuously

# def start_scheduler():
#     scheduler = Scheduler()
#     scheduler.every(86400).seconds.do(func) 
#     scheduler.run_continuously()