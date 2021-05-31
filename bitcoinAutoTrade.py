import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

#Access and Secret Key
access = "wvwHae1CPfhgjBTugAm3xu3PijbpXEy0jWNj7vnI"
secret = "w3lalAWfTAiv9NR6cgftAIJyAKFHVZHZaRgi39zl"

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

predicted_close_price = 0
def predict_price(ticker):
    global predicted_close_price
    data = prophet(ticker)[0]
    forecast = prophet(ticker)[1]
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

def get_start_time(ticker):
    """시작 시간 조회"""
    #df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    df = pyupbit.get_daily_ohlcv_from_base("KRW-BTC", base=0)
    start_time = df.index[-1]
    return start_time


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #start at midnight
        end_time = start_time + datetime.timedelta(hours=16)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            print("under if")
            target_price = get_target_price("KRW-BTC", 0.1)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    print("bought")
        else:
            print("under else")
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
                print("sold")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)