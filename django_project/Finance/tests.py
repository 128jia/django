from django.test import TestCase

import yfinance as yf
# stock = yf.download('GLD AAPL',start='2022-03-04',end='2022-05-19')      
# print(stock.index)
aapl_data = yf.download('AAPL', start='2021-01-01', end='2024-01-01')
gld_data = yf.download('GLD', start='2021-01-01', end='2024-01-01')

# 保留日期信息并重置索引
aapl_data = aapl_data[['Close']].reset_index()
print(aapl_data['Date'])
print('------------------------------------------')
print( aapl_data.index )
aapl_data['Date'] = aapl_data['Date'].dt.strftime('%Y-%m-%d')
print('------------------------------------------')
print(aapl_data['Date'])
# gld_data = gld_data[['Close']].reset_index()
# gld_data['Date'] = gld_data.index.dt.strftime('%Y-%m-%d')

# print('------------------------------------------')

# PERIOO = yf.download('GLD AAPL',period='6mo',interval='1mo')  # period=日期範圍 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max) ,interval=頻率 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)
# print (PERIOO[['Adj Close']])