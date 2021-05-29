import pyupbit
import datetime

access = "wvwHae1CPfhgjBTugAm3xu3PijbpXEy0jWNj7vnI"          # 본인 값으로 변경
secret = "w3lalAWfTAiv9NR6cgftAIJyAKFHVZHZaRgi39zl"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-BTC"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회

df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1)
start_time = df.index[0] + datetime.timedelta(hours = 15)
print(start_time)
value=0
def test():
    global value
    value = 1
test()
print(datetime.datetime.now())