from bs4 import BeautifulSoup
import requests
import math
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import yfinance as yf
import warnings
import time
from Investments.models import StockData
from schedule import Scheduler
import threading
import time
import pandas as pd
from tradingview_ta import TA_Handler, Interval, Exchange


warnings.simplefilter('ignore', ConvergenceWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARMA',FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA',FutureWarning)
def getDataFrame(scheme_code):
    def decorate(func):
        def decorated(*args,**kwargs):
            df = yf.download(str(scheme_code)+".NS",period='max')
            df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])
            df = df.rename(columns={'Close': 'nav'})
            df.reset_index(inplace=True)
            df['date'] = df['Date'].dt.strftime('%Y-%m-%d')

            info = yf.Ticker(str(scheme_code)+".NS").get_info()
            details = {'scheme_name': info['longName'], 'scheme_code': str(scheme_code)}
            return func(df,details)
        return decorated
    return decorate


def data_frame(func):
    def decorated(*args,**kwargs):
        df = yf.download(str(*args) + ".NS", period='max')
        df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])
        df = df.rename(columns={'Close': 'nav'})
        df.reset_index(inplace=True)
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        info = yf.Ticker(str(*args) + ".NS").get_info()
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

def ns():
    '''Name to Symbol mapped dictionary'''
    df=None
    with open("symbol.csv","r") as f:
        df=pd.read_csv(f)
    conv=df.iloc[:,:2]
    # print(conv)
    result_dict = dict(zip(conv.iloc[:, 1], conv.iloc[:, 0]))
    dict2={}
    for x,y in result_dict.items():
        dict2[x.strip().upper()]=y.strip().upper()
    return dict2

def rsi_(data, window=14):
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def func():
    large="https://www.moneyworks4me.com/best-index/top-stocks/top-large-cap-companies-list/"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }
    r=requests.get(large,headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    a=soup.find(id="table-data")
    x=a.find_all(class_="countRow")
    dict=ns()
    nifty="https://www.moneyworks4me.com/best-index/nse-stocks/top-nifty50-companies-list/"
    r=requests.get(nifty,headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    a=soup.find(id="stock-list-table")
    xx=a.find_all(class_="countRow")
    StockData.objects.all().delete()
    nifty50=[]
    niftybank=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-bank/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftybank.append(y)
    niftyIT=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-it/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftyIT.append(y)
    for i in xx:
        y=i.find(class_="company-ellipses").text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        nifty50.append(y)
    niftynext50=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-next-50/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftynext50.append(y)
    niftyfmcg=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-fmcg/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftyfmcg.append(y)

    niftyauto=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-auto/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftyauto.append(y)
    niftypharma=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-pharma/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftypharma.append(y)
    niftyenergy=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-energy/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftyenergy.append(y)
    niftyhealthcare=[]
    r=requests.get("https://dhan.co/nifty-stocks-list/nifty-healthcare/",headers=headers)
    soup=BeautifulSoup(r.content,'html5lib')
    ele=soup.find(class_="d-flex flex-wrap pl-5 mt-4")
    for i in ele:
        y=i.text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        niftyhealthcare.append(y)
        
    for i in x:
       try: 
        y=i.find(class_="company-ellipses").text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        sym=dict.get(y.strip().upper())
        isnifty50=False
        if y in nifty50:
            isnifty50=True
        isniftybank=False
        if y in niftybank:
            isniftybank=True
        isniftyIT=False
        if y in niftyIT:
            isniftyIT=True
        isniftyfmcg=False
        if y in niftyfmcg:
            isniftyfmcg=True
        isniftyauto=False
        if y in niftyauto:
            isniftyauto=True
        isniftypharma=False
        if y in niftypharma:
            isniftypharma=True
        isniftyenergy=False
        if y in niftyenergy:
            isniftyenergy=True
        isniftyhealthcare=False
        if y in niftyhealthcare:
            isniftyhealthcare=True
        isniftynext50=False
        if y in niftynext50:
            isniftynext50=True
        category='l'
        try:
            data=yf.Ticker(sym+'.NS').get_info()
        except:
            continue
        price=data.get('previousClose')
        if not price:price=0
        pe=data.get('trailingPE')
        if not pe:pe=0
        pb=data.get('priceToBook')
        if not pb:pb=0
        roe=data.get('returnOnEquity')
        if not roe:roe=0
        doe=data.get('debtToEquity')
        if not doe:doe=0
        enterpriseToEbitda=data.get('enterpriseToEbitda')
        if not enterpriseToEbitda:enterpriseToEbitda=0
        week52low=data.get('fiftyTwoWeekLow')
        if not week52low:week52low=0
        week52high=data.get('fiftyTwoWeekHigh')
        if not week52high:week52high=0
        dividendYield=data.get('dividendYield')
        if not dividendYield:dividendYield=0
        esg=0
        headers={
            'User-Agent':'Mozilla/5.0'
        }
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/sustainability?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        esg=100
        try:
            esg=int(soup.find(class_="Fz(36px) Fw(600) D(ib) Mend(5px)").text.strip())
        except:
            esg=100
        ma50=0
        ma200=0
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/key-statistics?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        try:
            ma50=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[14].text.strip().split(',')))
            ma200=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[15].text.strip().split(',')))
        except:
            pass
        rsi=rsi_(yf.download(sym+'.NS', period='max'))
        rsi=float(rsi.iloc[-1])
        ta='n'
        d={
            'BUY':'b',
            'SELL':'s',
            'NEUTRAL':'n',
            'STRONG_BUY':'sb',
            'STRONG_SELL':'ss',
        }
        
        handler = TA_Handler(
            symbol=sym,
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_MONTH,
        )
        ta2=handler.get_analysis().summary.get('RECOMMENDATION')
        analysis = d[ta2]
        rating=0
        tot=0
        tot+=5
        if pe<=10:
            rating+=5
        elif pe<=15:
            rating+=4
        elif pe<=26:
            rating+=3
        elif pe<32:
            rating+=2
        else:
            rating+=1
        tot+=5
        if pb<=1:
            rating+=5
        elif pb<=3:
            rating+=4
        elif pb<=5:
            rating+=3
        elif pb<9:
            rating+=2
        else:
            rating+=1
        tot+=5
        if not roe:
            roe=0
        if roe>=20:
            rating+=5
        elif roe>=15:
            rating+=4
        elif roe>=10:
            rating+=3
        elif roe>5:
            rating+=2
        else:
            rating+=1
        tot+=5
        if isnifty50:
            rating+=5
        tot+=3
        tot+=4
        if isniftynext50:
            rating+=4
        if isniftybank or isniftyIT or isniftyfmcg or isniftyauto or isniftypharma or isniftyenergy or isniftyhealthcare:
            rating+=3
        tot+=5
        if doe<=0.5:
            rating+=5
        elif doe<=1:
            rating+=4
        elif doe<=2:
            rating+=3
        elif doe<=3:
            rating+=2
        else:
            rating+=1
        tot+=5
        if enterpriseToEbitda<=10:
            rating+=5
        elif enterpriseToEbitda<=15:
            rating+=4
        elif enterpriseToEbitda<=20:
            rating+=3
        elif enterpriseToEbitda<=25:
            rating+=2
        else:
            rating+=1
        buysignal=0
        tot+=5
        if dividendYield>=5:
            rating+=5
        elif dividendYield>=3:
            rating+=4
        elif dividendYield>=2:
            rating+=3
        elif dividendYield>=1:
            rating+=2
        else:
            rating+=1
        tot+=5
        if esg ==100:
            tot-=5
        if esg <10:
            rating+=5
        elif esg<20:
            rating+=4
        elif esg<30:
            rating+=3
        elif esg<40:
            rating+=2
        else:
            if esg >99:
                rating+=0
            else:
                rating+=1
        rating=rating/tot*5
        tot=0
        tot+=5
        if price>=week52low*1.5:
            buysignal+=5
        elif price>=week52low*1.25:
            buysignal+=4
        elif price>=week52low*1.1:
            buysignal+=3
        elif price>=week52low*0.9:
            buysignal+=2
        else:
            buysignal+=1
        tot+=4
        if ma50>=ma200:
            buysignal+=4
        else:
            buysignal+=2
        if price > ma50:
            buysignal+=4
        else:
            buysignal+=2
        tot+=5
        if rsi<=30:
            buysignal+=5
        elif rsi<=40:
            buysignal+=4
        elif rsi<=60:
            buysignal+=3
        elif rsi<=70:
            buysignal+=2
        else:
            buysignal+=1
        tot+=15
        if analysis=='sb':
            buysignal+=15
        elif analysis=='b':
            buysignal+=10
        elif analysis=='n':
            buysignal+=5
        elif analysis=='s':
            buysignal-=1
        else:
            buysignal-=5
        buysignal=buysignal/tot*5
        # print(y)
        StockData.objects.create(name=y,symbol=sym,nifty50=isnifty50,niftybank=isniftybank,niftyit=isniftyIT,niftyfmcg=isniftyfmcg,niftypharma=isniftypharma,niftyauto=isniftyauto,niftyenergy=isniftyenergy,niftynext50=isniftynext50,niftyhealthcare=isniftyhealthcare,category='l',price=price,ESG=esg,ma50=ma50,ma200=ma200,pe=pe,pb=pb,roe=roe,doe=doe,enterpriseToEbitda=enterpriseToEbitda,week52low=week52low,week52high=week52high,dividendYield=dividendYield,rsi=rsi,ta=ta2,rating=rating,buysignal=buysignal)
       except Exception as e:
           with open("cron_log.log",'a') as f:
               f.write(str(e)+'\n')
    
    
    
    
    mid="https://www.moneyworks4me.com/best-index/top-stocks/top-mid-cap-companies-list/"
    r=requests.get(mid,headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    a=soup.find(id="table-data")
    x=a.find_all(class_="countRow")
    for i in x:
       try: 
        y=i.find(class_="company-ellipses").text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        sym=dict.get(y.strip().upper())
        isnifty50=False
        if y in nifty50:
            isnifty50=True
        isniftybank=False
        if y in niftybank:
            isniftybank=True
        isniftyIT=False
        if y in niftyIT:
            isniftyIT=True
        isniftyfmcg=False
        if y in niftyfmcg:
            isniftyfmcg=True
        isniftyauto=False
        if y in niftyauto:
            isniftyauto=True
        isniftypharma=False
        if y in niftypharma:
            isniftypharma=True
        isniftyenergy=False
        if y in niftyenergy:
            isniftyenergy=True
        isniftyhealthcare=False
        if y in niftyhealthcare:
            isniftyhealthcare=True
        isniftynext50=False
        if y in niftynext50:
            isniftynext50=True
        category='l'
        data=yf.Ticker(sym+'.NS').get_info()
        price=data.get('previousClose')
        if not price:price=0
        pe=data.get('trailingPE')
        if not pe:pe=0
        pb=data.get('priceToBook')
        if not pb:pb=0
        roe=data.get('returnOnEquity')
        if not roe:roe=0
        doe=data.get('debtToEquity')
        if not doe:doe=0
        enterpriseToEbitda=data.get('enterpriseToEbitda')
        if not enterpriseToEbitda:enterpriseToEbitda=0
        week52low=data.get('fiftyTwoWeekLow')
        if not week52low:week52low=0
        week52high=data.get('fiftyTwoWeekHigh')
        if not week52high:week52high=0
        dividendYield=data.get('dividendYield')
        if not dividendYield:dividendYield=0
        esg=0
        headers={
            'User-Agent':'Mozilla/5.0'
        }
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/sustainability?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        esg=100
        try:
            esg=int(soup.find(class_="Fz(36px) Fw(600) D(ib) Mend(5px)").text.strip())
        except:
            esg=100
        ma50=0
        ma200=0
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/key-statistics?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        try:
            ma50=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[14].text.strip().split(',')))
            ma200=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[15].text.strip().split(',')))
        except:
            pass
        rsi=rsi_(yf.download(sym+'.NS', period='max'))
        rsi=float(rsi.iloc[-1])
        ta='n'
        d={
            'BUY':'b',
            'SELL':'s',
            'NEUTRAL':'n',
            'STRONG_BUY':'sb',
            'STRONG_SELL':'ss',
        }
        handler = TA_Handler(
            symbol=sym,
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_MONTH,
        )
        ta2=handler.get_analysis().summary.get('RECOMMENDATION')
        analysis = d[ta2]
        rating=0
        tot=0
        tot+=5
        if pe<=10:
            rating+=5
        elif pe<=15:
            rating+=4
        elif pe<=26:
            rating+=3
        elif pe<32:
            rating+=2
        else:
            rating+=1
        tot+=5
        if pb<=1:
            rating+=5
        elif pb<=3:
            rating+=4
        elif pb<=5:
            rating+=3
        elif pb<9:
            rating+=2
        else:
            rating+=1
        tot+=5
        if roe>=20:
            rating+=5
        elif roe>=15:
            rating+=4
        elif roe>=10:
            rating+=3
        elif roe>5:
            rating+=2
        else:
            rating+=1
        tot+=5
        if isnifty50:
            rating+=5
        tot+=3
        tot+=4
        if isniftynext50:
            rating+=4
        if isniftybank or isniftyIT or isniftyfmcg or isniftyauto or isniftypharma or isniftyenergy or isniftyhealthcare:
            rating+=3
        tot+=5
        if doe<=0.5:
            rating+=5
        elif doe<=1:
            rating+=4
        elif doe<=2:
            rating+=3
        elif doe<=3:
            rating+=2
        else:
            rating+=1
        tot+=5
        if enterpriseToEbitda<=10:
            rating+=5
        elif enterpriseToEbitda<=15:
            rating+=4
        elif enterpriseToEbitda<=20:
            rating+=3
        elif enterpriseToEbitda<=25:
            rating+=2
        else:
            rating+=1
        buysignal=0
        tot+=5
        if dividendYield>=5:
            rating+=5
        elif dividendYield>=4:
            rating+=4
        elif dividendYield>=2:
            rating+=3
        elif dividendYield>=1:
            rating+=2
        else:
            rating+=1
        tot+=5
        if esg ==100:
            tot-=5
        if esg <10:
            rating+=5
        elif esg<20:
            rating+=4
        elif esg<30:
            rating+=3
        elif esg<40:
            rating+=2
        else:
            if esg >99:
                rating+=0
            else:
                rating+=1
        rating=rating/tot*5
        tot=0
        tot+=5
        if price>=week52low*1.5:
            buysignal+=5
        elif price>=week52low*1.25:
            buysignal+=4
        elif price>=week52low*1.1:
            buysignal+=3
        elif price>=week52low*0.9:
            buysignal+=2
        else:
            buysignal+=1
        tot+=4
        if ma50>=ma200:
            buysignal+=4
        else:
            buysignal+=2
        if price > ma50:
            buysignal+=4
        else:
            buysignal+=2
        tot+=5
        if rsi<=30:
            buysignal+=5
        elif rsi<=40:
            buysignal+=4
        elif rsi<=60:
            buysignal+=3
        elif rsi<=70:
            buysignal+=2
        else:
            buysignal+=1
        tot+=15
        if analysis=='sb':
            buysignal+=15
        elif analysis=='b':
            buysignal+=10
        elif analysis=='n':
            buysignal+=5
        elif analysis=='s':
            buysignal-=1
        else:
            buysignal-=5
        buysignal=buysignal/tot*5
        # print(y)
        StockData.objects.create(name=y,symbol=sym,nifty50=isnifty50,niftybank=isniftybank,niftyit=isniftyIT,niftyfmcg=isniftyfmcg,niftypharma=isniftypharma,niftyauto=isniftyauto,niftyenergy=isniftyenergy,niftynext50=isniftynext50,niftyhealthcare=isniftyhealthcare,category='m',price=price,ESG=esg,ma50=ma50,ma200=ma200,pe=pe,pb=pb,roe=roe,doe=doe,enterpriseToEbitda=enterpriseToEbitda,week52low=week52low,week52high=week52high,dividendYield=dividendYield,rsi=rsi,ta=ta2,rating=rating,buysignal=buysignal)
       except Exception as e:
            with open("cron_log.log",'a') as f:
                f.write(str(e)+'\n')
    
    small="https://www.moneyworks4me.com/best-index/top-stocks/top-small-cap-companies-list/"  
    r=requests.get(small,headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    a=soup.find(id="table-data")
    x=a.find_all(class_="countRow")
    for i in x:
       try: 
        y=i.find(class_="company-ellipses").text.strip()
        if "Ltd" in y:
            y=(y[:-3]+"Limited")
        else:
            pass
        sym=dict.get(y.strip().upper())
        isnifty50=False
        if y in nifty50:
            isnifty50=True
        isniftybank=False
        if y in niftybank:
            isniftybank=True
        isniftyIT=False
        if y in niftyIT:
            isniftyIT=True
        isniftyfmcg=False
        if y in niftyfmcg:
            isniftyfmcg=True
        isniftyauto=False
        if y in niftyauto:
            isniftyauto=True
        isniftypharma=False
        if y in niftypharma:
            isniftypharma=True
        isniftyenergy=False
        if y in niftyenergy:
            isniftyenergy=True
        isniftyhealthcare=False
        if y in niftyhealthcare:
            isniftyhealthcare=True
        isniftynext50=False
        if y in niftynext50:
            isniftynext50=True
        
        category='l'
        data=yf.Ticker(sym+'.NS').get_info()
        price=data.get('previousClose')
        if not price:price=0
        pe=data.get('trailingPE')
        if not pe:pe=0
        pb=data.get('priceToBook')
        if not pb:pb=0
        roe=data.get('returnOnEquity')
        if not roe:roe=0
        doe=data.get('debtToEquity')
        if not doe:doe=0
        enterpriseToEbitda=data.get('enterpriseToEbitda')
        if not enterpriseToEbitda:enterpriseToEbitda=0
        week52low=data.get('fiftyTwoWeekLow')
        if not week52low:week52low=0
        week52high=data.get('fiftyTwoWeekHigh')
        if not week52high:week52high=0
        dividendYield=data.get('dividendYield')
        if not dividendYield:dividendYield=0
        esg=0
        headers={
            'User-Agent':'Mozilla/5.0'
        }
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/sustainability?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        esg=100
        try:
            esg=int(soup.find(class_="Fz(36px) Fw(600) D(ib) Mend(5px)").text.strip())
        except:
            esg=100
        ma50=0
        ma200=0
        r=requests.get(f'https://finance.yahoo.com/quote/{sym}.NS/key-statistics?p={sym}.NS',headers=headers)
        soup=BeautifulSoup(r.content,'html5lib')
        try:
            ma50=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[14].text.strip().split(',')))
            ma200=float(''.join(soup.find_all(class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[15].text.strip().split(',')))
        except:
            pass
        rsi=rsi_(yf.download(sym+'.NS', period='max'))
        rsi=float(rsi.iloc[-1])
        ta='n'
        d={
            'BUY':'b',
            'SELL':'s',
            'NEUTRAL':'n',
            'STRONG_BUY':'sb',
            'STRONG_SELL':'ss',
        }
        
        handler = TA_Handler(
            symbol=sym,
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_MONTH,
        )
        ta2=handler.get_analysis().summary.get('RECOMMENDATION')
        analysis = d[ta2]
        rating=0
        tot=0
        tot+=5
        if pe<=10:
            rating+=5
        elif pe<=15:
            rating+=4
        elif pe<=26:
            rating+=3
        elif pe<32:
            rating+=2
        else:
            rating+=1
        tot+=5
        if pb<=1:
            rating+=5
        elif pb<=3:
            rating+=4
        elif pb<=5:
            rating+=3
        elif pb<9:
            rating+=2
        else:
            rating+=1
        tot+=5
        if roe>=20:
            rating+=5
        elif roe>=15:
            rating+=4
        elif roe>=10:
            rating+=3
        elif roe>5:
            rating+=2
        else:
            rating+=1
        tot+=5
        if isnifty50:
            rating+=5
        tot+=3
        tot+=4
        if isniftynext50:
            rating+=4
        if isniftybank or isniftyIT or isniftyfmcg or isniftyauto or isniftypharma or isniftyenergy or isniftyhealthcare:
            rating+=3
        tot+=5
        if doe<=0.5:
            rating+=5
        elif doe<=1:
            rating+=4
        elif doe<=2:
            rating+=3
        elif doe<=3:
            rating+=2
        else:
            rating+=1
        tot+=5
        if enterpriseToEbitda<=10:
            rating+=5
        elif enterpriseToEbitda<=15:
            rating+=4
        elif enterpriseToEbitda<=20:
            rating+=3
        elif enterpriseToEbitda<=25:
            rating+=2
        else:
            rating+=1
        buysignal=0
        tot+=5
        if dividendYield>=5:
            rating+=5
        elif dividendYield>=4:
            rating+=4
        elif dividendYield>=2:
            rating+=3
        elif dividendYield>=1:
            rating+=2
        else:
            rating+=1
        tot+=5
        if esg ==100:
            tot-=5
        if esg <10:
            rating+=5
        elif esg<20:
            rating+=4
        elif esg<30:
            rating+=3
        elif esg<40:
            rating+=2
        else:
            if esg >99:
                rating+=0
            else:
                rating+=1
        rating=rating/tot*5
        tot=0
        tot+=5
        if price>=week52low*1.5:
            buysignal+=5
        elif price>=week52low*1.25:
            buysignal+=4
        elif price>=week52low*1.1:
            buysignal+=3
        elif price>=week52low*0.9:
            buysignal+=2
        else:
            buysignal+=1
        tot+=4
        if ma50>=ma200:
            buysignal+=4
        else:
            buysignal+=2
        if price > ma50:
            buysignal+=4
        else:
            buysignal+=2
        tot+=5
        if rsi<=30:
            buysignal+=5
        elif rsi<=40:
            buysignal+=4
        elif rsi<=60:
            buysignal+=3
        elif rsi<=70:
            buysignal+=2
        else:
            buysignal+=1
        tot+=15
        if analysis=='sb':
            buysignal+=15
        elif analysis=='b':
            buysignal+=10
        elif analysis=='n':
            buysignal+=5
        elif analysis=='s':
            buysignal-=1
        else:
            buysignal-=5
        buysignal=buysignal/tot*5
        # print(y)
        StockData.objects.create(name=y,symbol=sym,nifty50=isnifty50,niftybank=isniftybank,niftyit=isniftyIT,niftyfmcg=isniftyfmcg,niftypharma=isniftypharma,niftyauto=isniftyauto,niftyenergy=isniftyenergy,niftynext50=isniftynext50,niftyhealthcare=isniftyhealthcare,category='s',price=price,ESG=esg,ma50=ma50,ma200=ma200,pe=pe,pb=pb,roe=roe,doe=doe,enterpriseToEbitda=enterpriseToEbitda,week52low=week52low,week52high=week52high,dividendYield=dividendYield,rsi=rsi,ta=ta2,rating=rating,buysignal=buysignal)
       except Exception as e:
            with open("cron_log.log",'a') as f:
                f.write(str(e)+'\n')
                
                

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
    scheduler.every(86400).seconds.do(func) 
    scheduler.run_continuously()