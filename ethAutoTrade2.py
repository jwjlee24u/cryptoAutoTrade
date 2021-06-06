import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

#Access and Secret Key
access = "wvwHae1CPfhgjBTugAm3xu3PijbpXEy0jWNj7vnI"
secret = "w3lalAWfTAiv9NR6cgftAIJyAKFHVZHZaRgi39zl"
end_hour1 = 24
#end_hour2 = 10
coin = "KRW-ETH"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    #2일치를 검색. 오늘 종가 = 다음날 시가
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_price_10min_before(ticker):
    return pyupbit.get_ohlcv(ticker, interval="minute10", count=1)["close"][0]

def get_price_30min_before(ticker):
    return pyupbit.get_ohlcv(ticker, interval="minute30", count=1)["close"][0]

# 로그인 with ur own acess and secret key
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

def prophet(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    return [data, forecast]

predicted_close_price1 = 0
def predict_price1(ticker):
    global predicted_close_price1
    data = prophet(ticker)[0]
    forecast = prophet(ticker)[1]
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=0)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=0)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price1 = closeValue
predict_price1(coin)
schedule.every(10).minutes.do(lambda: predict_price1(coin))

# predicted_close_price2 = 0
# def predict_price2(ticker):
#     global predicted_close_price2
#     data = prophet(ticker)[0]
#     forecast = prophet(ticker)[1]
#     closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=end_hour2)]
#     if len(closeDf) == 0:
#         closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=end_hour2)]
#     closeValue = closeDf['yhat'].values[0]
#     predicted_close_price2 = closeValue
# predict_price2(coin)
# schedule.every(10).minutes.do(lambda: predict_price2(coin))

def get_start_time1(ticker):
    """시작 시간 조회"""
    #df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=0)
    start_time = df.index[-1]
    return start_time

# def get_start_time2(ticker):
#     """시작 시간 조회"""
#     #df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
#     df = pyupbit.get_daily_ohlcv_from_base(ticker, base=12)
#     start_time = df.index[-1]
#     return start_time



# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time1 = get_start_time1(coin) #start at midnight
        end_time1 = start_time1 + datetime.timedelta(hours=end_hour1)
        # start_time2 = get_start_time2(coin) #start at midnight
        # end_time2 = start_time2 + datetime.timedelta(hours=end_hour2)
        schedule.run_pending()
        print("start1: " + str(start_time1))
        print("end1: " + str(end_time1))

        if start_time1 < now < end_time1 - datetime.timedelta(seconds=10):
            print("under 1")            
            target_price = get_target_price(coin, 0.1)
            current_price = get_current_price(coin)
            print("current price: " + str(current_price), "target price: " + str(target_price), "predicted_close_price1: " + str(predicted_close_price1))
            if target_price < current_price and current_price < predicted_close_price1:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(coin, krw*0.9995)
                    print("bought at 1")
                if (get_price_10min_before(coin) - current_price) / get_price_10min_before(coin) > 0.015 or (get_price_30min_before(coin) - current_price) / get_price_30min_before(coin) > 0.015:
                    upbit.sell_market_order(coin, eth*0.9995)
                    print("sold")
                    time.sleep(3600)    
        else:
            print("under else")
            eth = get_balance("ETH")
            if eth > 0.00008:
                upbit.sell_market_order(coin, eth*0.9995)
                print("sold")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)