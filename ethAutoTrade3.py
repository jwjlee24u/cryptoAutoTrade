import time
import pyupbit
import datetime
import schedule

access = "wvwHae1CPfhgjBTugAm3xu3PijbpXEy0jWNj7vnI"
secret = "w3lalAWfTAiv9NR6cgftAIJyAKFHVZHZaRgi39zl"
coin = "KRW-ETH"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

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

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_price_10min_before(ticker):
    return pyupbit.get_ohlcv(ticker, interval="minute10", count=1)["open"][0]

def get_price_30min_before(ticker):
    return pyupbit.get_ohlcv(ticker, interval="minute30", count=1)["open"][0]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
price_bought = 0

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coin)
        end_time = start_time + datetime.timedelta(days=1)
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(coin, 0.5)
            current_price = get_current_price(coin)
            ma15 = get_ma15(coin)
            print("current price: " + str(current_price), "target price: " + str(target_price), "ma15: " + str(ma15))
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                print("under if")
                if krw > 5000:
                    upbit.buy_market_order(coin, krw*0.9995)
                    price_bought = current_price
                    print("bought at " + str(current_price))
                if (get_price_10min_before(coin) - current_price) / get_price_10min_before(coin) > 0.015 or (get_price_30min_before(coin) - current_price) / get_price_30min_before(coin) > 0.015:                    
                    eth = get_balance("ETH")
                    upbit.sell_market_order(coin, eth*0.9995)
                    print("sold at " + str(current_price))
                    time.sleep(3600)
                if current_price < price_bought:
                    eth = get_balance("ETH")
                    upbit.sell_market_order(coin, eth*0.9995)
                    print("sold at " + str(current_price))
                    time.sleep(3600)
        else:
            eth = get_balance("ETH")
            if eth > 0.00008:
                upbit.sell_market_order(coin, eth*0.9995)
                print("sold")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)