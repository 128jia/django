from django.test import TestCase

# Create your tests here.
import yfinance as yf
stock = yf.download('GLD AAPL',start='2021-01-01',end='2024-01-01')      
print(stock)
print('------------------------------------------')

PERIOO = yf.download('GLD AAPL',period='6mo',interval='1mo')  # period=日期範圍 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max) ,interval=頻率 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)
#print (PERIOO)
