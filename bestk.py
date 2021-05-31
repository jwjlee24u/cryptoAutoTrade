import pyupbit
import numpy as np
import datetime

today = datetime.date.today()
def get_ror(k=0.5):
    # #df = pyupbit.get_ohlcv("KRW-BTC", count=10)
    # df = pyupbit.get_daily_ohlcv_from_base("KRW-BTC", base=2)
    # df['range'] = (df['high'] - df['low']) * k
    # df['target'] = df['open'] + df['range'].shift(1)
    yesterday = today - datetime.timedelta(days = 1)
    df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=17, to=str(yesterday)+" 17:00") #str(today)+" 18:00"
    # #from 9am add by "18" hours
    target = df.iloc[-1]['close'] + (df['high'].max() - df['low'].min()) * k
    # df['range'] = (df['high'] - df['low']) * k
    # df['target'] = df['open'] + df['range'].shift(1)
    #print(df['target'])
    # fee = 0.0032
    # df['ror'] = np.where(df['high'] > df['target'],
    #                      df['close'] / df['target'],
    #                      #df['close'] / df['target'] - fee,
    #                      1)
    df['ror'] = np.where(df['high'].max() > target,
                         df.iloc[-1]['close'] / target,
                         #df['close'] / df['target'] - fee,
                         1)
    print(df['high'].max(), df.iloc[-1]['close'], target)
    ror = df['ror'].cumprod()[-2]
    return ror


for k in np.arange(0.1, 1.0, 0.01):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))