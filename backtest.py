import pyupbit
import numpy as np

#OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
df = pyupbit.get_ohlcv("KRW-BTC", count=7) #count=7 (shows data for 7 days)

#변동폭(=고가-저가) * k값 계산
k = 0.5
df['range'] = (df['high'] - df['low']) * k

#target(타깃 매수가), range는 어제자 변동폭 * k 값이기에 column을 한칸씩 내림(다음날거에 적용)
df['target'] = df['open'] + df['range'].shift(1)

#수수료
#fee = 0.0032

#수익률 = ror, np. where(조건문, value when ture, vlaue when false)
#if highest value is greater than target
#TRUE: the rate of profit is the close value / target value
#FALSE: NO transaction --> thus, no change
df['ror'] = np.where(df['high'] > df['target'], 
                     #df['close'] / df['target'] - fee,
                     df['close'] / df['target'], 
                     1)

#누적수익률, cumprod = 누적곱계산 (cumulative product)
df['hpr'] = df['ror'].cumprod()

#하락폭(Draw Down) 계산 (누적 최대 값과 현재 누적수익률 (hpr) 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#Max DD 하락폭의 최대값
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")
