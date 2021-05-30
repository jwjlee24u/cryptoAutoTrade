import pyupbit
import datetime

access = "wvwHae1CPfhgjBTugAm3xu3PijbpXEy0jWNj7vnI"          # 본인 값으로 변경
secret = "w3lalAWfTAiv9NR6cgftAIJyAKFHVZHZaRgi39zl"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-BTC"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회

df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1)
start_time = df.index[0] + datetime.timedelta(hours = 14)
print(start_time)
end = start_time + datetime.timedelta(hours = 18)
print(end)

val1 = 0
val2 = 1
def test():
    global val1, val2
    val1 = 2
    val2 = 0
test()
print(val1, val2)