import os
import math
import requests
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
import warnings
from binance.client import Client
from binance.enums import *
warnings.simplefilter(action='ignore', category=FutureWarning)
# Nadarya variables
l = []
w = []
ws = 0
s = 0
for i in range(500):
  l=l+[i]
  gaus=[math.exp(-(math.pow(i,2)/(40.5)))]
  ws+=gaus[0]
  w=w+gaus

symbols = ["FETUSDT","JOEUSDT","RNDRUSDT"]

# Nadarya function
def nad(row, index,cdf):
    sum= 0
    j = 500
    for i in range(index-1 , index - 500, -1):
        j -= 1
        current=cdf.iloc[i]
        sum+=current['Close']*w[j]
    out = sum / ws
    sume1 = abs(row - out)
    mae = sume1 / (4.5 * 2.5)
    u = row + mae
    l = row - mae
    return float(u), float(l)

def binance(s):
    api_key='driaBQg3PSsqotcuKgC9WqeDTmOjp59eGKLOo88pGevkfNyer2Ig3eHMwaqJwMp9'
    symbol = s  

    # Binance API endpoint for historical K-line data
    api_url = 'https://api.binance.com/api/v3/klines'

    # Calculate the timestamp for the start time (current time - 500 hours)
    start_time = int((datetime.utcnow() - timedelta(hours=502)).timestamp()) * 1000
    start_time = start_time 
    params = {
        'symbol': symbol,
        'interval': '1h',  # Fetch data hourly
        'startTime': start_time,
        'limit': 502 # Number of candles
    }
    df_hourly = pd.DataFrame(columns=['Time', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume'])

    # Make the API request
    response = requests.get(api_url, params=params, headers={'X-MBX-APIKEY': api_key})

    if response.status_code == 200:
        data = response.json()

        # Process the data and append it to the df_hourly DataFrame
        for kline in data:
            open_time = datetime.utcfromtimestamp(kline[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            # Append the data to the DataFrame
            df_hourly = df_hourly.append({
                'Time': open_time,
                'Symbol': symbol,
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume,
                'ema':None,
                'upper_band':None,
                'lower_band':None
            }, ignore_index=True)
        return df_hourly


    else:
        print(f"Error {response.status_code}: {response.text}")
        return None 



def get_binance_prices(df_hourly,s):
    api_key='driaBQg3PSsqotcuKgC9WqeDTmOjp59eGKLOo88pGevkfNyer2Ig3eHMwaqJwMp9'
    symbol = s  

    # Binance API endpoint for historical K-line data
    api_url = 'https://api.binance.com/api/v3/klines'

    # Calculate the timestamp for the start time (current time - 500 hours)
    start_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp()) * 1000
    params = {
        'symbol': symbol,
        'interval': '1h',  # Fetch data hourly
        'startTime': start_time,
        'limit': 1  # Number of candles
    }

    # Make the API request
    response = requests.get(api_url, params=params, headers={'X-MBX-APIKEY': api_key})

    if response.status_code == 200:
        data = response.json()

        # Process the data and append it to the df_hourly DataFrame
        for kline in data:
            open_time = datetime.utcfromtimestamp(kline[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            # Append the data to the DataFrame
            df_hourly = df_hourly.append({
                'Time': open_time,
                'Symbol': symbol,
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume,
                'ema':None,
                'upper_band':None,
                'lower_band':None
            }, ignore_index=True)
            return df_hourly


# Fetch current ticker price
def fetch_ticker_data(symbol):
    api_key = 'driaBQg3PSsqotcuKgC9WqeDTmOjp59eGKLOo88pGevkfNyer2Ig3eHMwaqJwMp9'
    symbol = symbol
    api_url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}

    response = requests.get(api_url, params=params, headers={'X-MBX-APIKEY': api_key})

    if response.status_code == 200:
        data = response.json()
        current_price = float(data['price'])
        current_time = datetime.utcnow()
        return [current_time, current_price]
    else:
        return None

def emah(df,index):
    ema_value = df['High'].rolling(window=5, min_periods=1).mean().iloc[index]
    return float(ema_value)

def currentprice(symbol):
    base_url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad requests
    data = response.json()
    return float(data["price"])

#initiation 
trade=[]
in_trade=[]
dfl=[]
ema=[]
lower=[]
sl=[]
tp=[]
in_trade=[]
q=[]
m=1
for i in range (len(symbols)):
    dfl.append(binance(symbols[i]))
    q.append(32)
i=0
initial_df = pd.DataFrame(columns=['entry_price', 'entry_index', 'entry_time', 'sl', 'tp', 'exit_price', 'exit_time', 'exit_index'])


for f in dfl :
    sl.append(0)
    tp.append(0)
    trade.append(initial_df)
    in_trade.append(None)
    f['ema']=None
    row=f.tail(1)
    x,y=nad(row['Close'],len(f)-1,f)
    lower.append(y)
    z=len(dfl[i])-1
    dfl[i]['lower_band'].iloc[z]=y
    dfl[i]['upper_band'].iloc[z]=x
    dfl[i]['ema'] = dfl[i]['High'].ewm(span=5, adjust=False).mean()
    row=f.tail(1)
    ema.append(dfl[i]['ema'].iloc[-1])
    file_path = fr'C:\Users\uber\Desktop\hyper z\{symbols[i]}data.csv'
    if os.path.exists(file_path):
        os.remove(file_path)
    dfl[i].to_csv(file_path, index=False)
    print(dfl[i].tail(1))
    i+=1

key='RgYufFbMgbw6SHAH9kmYJJCEo0MbcThyqQa4Ak8zAuXZozVmoDlyG3uXc7p6hP8z'
secret='Z5y2tE0B5kVIwQilZuWFbZUHvQIPtoucZDTzvoA08LIqGPdpOvgXtyKQpnkjz3hA'
client=Client(key,secret)
runtime=0
tick=[4,4,3]
step=[0,2,2]

i=0
for i in range(len(symbols)):
    print("Step Size:", step[i])
    print("Tick Size:", tick[i])
order = {
    'symbol': None,
    'orderId': None,
    'orderListId': None,
    'clientOrderId': None,
    'transactTime': None,
    'price': None,
    'origQty': None,
    'executedQty': None,
    'cummulativeQuoteQty': None,
    'status': None,
    'timeInForce': None,
    'type': None,
    'side': None,
    'workingTime': None,
    'fills': None,
    'selfTradePreventionMode': None
}



m=1
while True:
    
    if in_trade[0]==None:
        for i in range(len(symbols)):
            row=dfl[i].tail(1)
            in_trade[i]="BUY"
            price=float(row['lower_band'])
            price=round(price,tick[i])

            quantity=float(q[i]*0.999)/price
            quantity=round(quantity,step[i])
            
            buy_limit = client.create_order(
             	symbol=symbols[i],
                side='BUY',
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=price)
            print(symbols[i])
            print(row)
            print(buy_limit)
            
    t=datetime.utcnow()
    if t.minute==0:
        #new hour orders
        i=0
        for symbol in symbols :
            dfl[i]=get_binance_prices(dfl[i],symbol)
            row=dfl[i].tail(1)
            o=row['Close']
            u,l=nad(o,len(dfl[i])-1,dfl[i])
            dfl[i].loc[dfl[i].index[-1], 'upper_band']=u
            dfl[i].loc[dfl[i].index[-1], 'lower_band']=l
            lower[i]=round(l,tick[i])
            last_row_index = dfl[i].index[-1]
            ema[i] = emah(dfl[i],last_row_index)
            ema[i]=round(ema[i],tick[i])
            dfl[i].loc[last_row_index, 'ema'] = ema[i]
            row=dfl[i].tail(1)
            #file saving 
            file_path = fr'C:\Users\uber\Desktop\BIN BOT\{symbol}data.csv'
            if os.path.exists(file_path):
                os.remove(file_path)
            dfl[i].to_csv(file_path, index=False)
            
            orders = client.get_all_orders(symbol=symbol, limit=1)
            orderid=orders[0]['orderId']
            
#buy side
            
            if (orders[0]['side']=='BUY' ):
                if orders[0]['status']=="FILLED":
                    quantity=float(orders[0]['origQty'])
                    quantity=round(quantity,step[i])
                    sl[i]=float(order[0]['price'])*0.98
                    sl[i]=round(sl[i],tick[i])
                    ema[i]=round(ema[i],tick[i])
                    current_price=current_price(symbol)
                    if current_price<= sl[i]:
                        print("Entry_price",orders[0]['price'])
                        order = client.order_market_sell(
                            symbol=symbol,
                            quantity=quantity)
                        print(symbol)
                        print(row)
                        price = float(order['fills'][0]['price'])
                        print("sl Exit_price:",price)
                    else :
                        buy_limit = client.create_order(
                         	symbol=symbols[i],
                            side='SELL',
                            type='LIMIT',
                            timeInForce='GTC',
                            quantity=quantity,
                            price=ema[i])
                        
                        
                            
                if orders[0]['status']=="NEW":
                    result = client.cancel_order(
                        symbol=symbol,
                        orderId=orderid)
                    price=float(row['lower_band'])
                    price=round(price,tick[i])
                    quantity=(q[i]*0.999)/price
                    quantity=round(quantity,step[i])
                    if step[i]==0:
                        quantity=int(quantity)
                    buy_limit = client.create_order(
                     	symbol=symbol,
    		            side='BUY',
    	            	type='LIMIT',
    		            timeInForce='GTC',
    		            quantity=quantity,
    		            price=price)
                    
                    
                   
                    in_trade[i]='buy'
                    
                    
#sell _side 
            
            if orders[0]['status']=="NEW" and orders[0]['side']=='SELL':
                
                quantity=float(orders[0]['origQty'])
                quantity=round(quantity,step[i])
                sl[i]=float(order[0]['price'])*0.98
                sl[i]=round(sl[i],tick[i])
                ema[i]=round(ema[i],tick[i])
                if step[i]==0:
                    quantity=int(quantity)
                result = client.cancel_order(
                    symbol=symbol,
                    orderId=orderid)
                buy_limit = client.create_order(
                 	symbol=symbol,
		            side='SELL',
	            	type='LIMIT',
		            timeInForce='GTC',
		            quantity=quantity,
		            price=ema[i])
                
               
                in_trade[i]='buy'
            
            if orders[0]['status']=="FILLED" and orders[0]['side']=='SELL':
                q[i]=float()
                price=float(row['lower_band'])
                price=round(price,tick[i])
                quantity=(q[i]*0.999)/price
                quantity=round(quantity,step[i])
                if step[i]==0:
                    quantity=int(quantity)
                buy_limit = client.create_order(
                 	symbol=symbol,
		            side='BUY',
	            	type='LIMIT',
		            timeInForce='GTC',
		            quantity=quantity,
		            price=price)
            
            i+=1
        time.sleep(60)
                    
    time.sleep(1)
    runtime += 1
    if (runtime%600)==0 :
        i=0
        for symbol in symbols:
            orders = client.get_all_orders(symbol=symbol, limit=1)
            orderid=orders[0]['orderId']
            current_price=currentprice(symbol)
            print(symbol)
            print(orders)
            
              #buy side
            if (orders[0]['side']=='BUY' ):
                if orders[0]['status']=="FILLED":
                    print(symbol)
                    print(ema[i])
                    print("entry_price",orders[0]['price'])
                    quantity=float(orders[0]['origQty'])*0.995
                    quantity=round(quantity,step[i])
                    print(quantity)
                    sl[i]=float(orders[0]['price'])*0.98
                    sl[i]=round(sl[i],tick[i])
                    ema[i]=round(ema[i],tick[i])
                    buy_limit = client.create_order(
                     	symbol=symbol,
    		            side='SELL',
    	            	type='LIMIT',
    		            timeInForce='GTC',
    		            quantity=quantity,
    		            price=ema[i])
                    
            if  current_price<= sl[i]and orders[0]['side']=='SELL':
                print(symbol)
                print("Entry_price",orders[0]['price'])
                order = client.order_market_sell(
                    symbol=symbol,
                    quantity=quantity)
                q[i]=float(order['cummulativeQuoteQty'])
                
                price = float(order['fills'][0]['price'])
                print("**Exit_price SL:",price)
                price =round(lower[i],tick[i])
                quantity=(q[i]*0.998)/price
                quantity=round(quantity,step[i])
                print('new entry :',symbol)
                
                if step[i]==0:
                    quantity=int(quantity)
                buy_limit = client.create_order(
                 	symbol=symbol,
		            side='BUY',
	            	type='LIMIT',
		            timeInForce='GTC',
		            quantity=quantity,
		            price=price)
                
                    
                        
                        
            if (orders[0]['side']=='SELL'):
                if orders[0]['status']=="FILLED":
                    q[i]=float(order['cummulativeQuoteQty'])
                    price =round(lower[i],tick[i])
                    quantity=(q[i]*0.998)/price
                    quantity=round(quantity,step[i])
                    print('new entry :')
                    print(quantity)
                    print(price)
                    print(quantity*price)
                    if step[i]==0:
                        quantity=int(quantity)
                    buy_limit = client.create_order(
                     	symbol=symbol,
    		            side='BUY',
    	            	type='LIMIT',
    		            timeInForce='GTC',
    		            quantity=quantity,
    		            price=price)
            
                        
            
            i+=1

            
            
            

            
                
                
        
    
       
            
            