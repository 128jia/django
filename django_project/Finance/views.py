from django.shortcuts import render
from django.http import HttpResponse #匯入http模組
import yfinance as yf 
from django.http import JsonResponse
import numpy as np
import pandas as pd

def hello_world(request):
    return HttpResponse("Hello World!")
# Create your views here.
def fetch(request):
    
    return render(request, 'F_home.html',locals())

def choose(request):
    
    return render(request, 'F_choose.html',locals())
def get_stock_data1(request):

    # 下载股票数据
    aapl_data = yf.download('AAPL', start='2021-01-01', end='2024-01-01')
    gld_data = yf.download('GLD', start='2021-01-01', end='2024-01-01')

    # 保留日期信息并重置索引
    aapl_data = aapl_data[['Close']].reset_index()
    aapl_data['Date'] = aapl_data['Date'].dt.strftime('%Y-%m-%d')
    gld_data = gld_data[['Close']].reset_index()
    gld_data['Date'] = gld_data['Date'].dt.strftime('%Y-%m-%d')

    # 将数据转换为字典
    aapl_stock_data = aapl_data.to_dict(orient='records')
    gld_stock_data = gld_data.to_dict(orient='records')

    # 计算 spread、滚动均值和滚动标准差
    aapl_log_close = np.log(aapl_data['Close'])
    gld_log_close = np.log(gld_data['Close'])
    ########### LOG ( GLD / AAPL ) ######## 
    spread = gld_log_close - aapl_log_close
    rolling_mean = spread.rolling(window=200).mean()
    rolling_std = spread.rolling(window=200).std()

    # 填充 NaN 值
    rolling_mean_filled = rolling_mean.bfill()
    rolling_std_filled = rolling_std.bfill()

    # 将日期与计算结果结合，保留日期信息
    spread_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': spread[i]} for i in range(len(spread))]
    rolling_mean_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': rolling_mean_filled[i]} for i in range(len(rolling_mean_filled))]
    rolling_std_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': rolling_std_filled[i]} for i in range(len(rolling_std_filled))]

    open_positions = []  # 记录开仓
    close_positions = []  # 记录关仓
    profit_table=[]
    #### profit 計算 ######
    cumulative_profit = 0  # 累積損益初始為 0
    daily_profits = []
    shares_aapl = 0  # 初始AAPL持倉單位
    shares_gld = 0  # 初始GLD持倉單位
    #######設立一開始未持倉
    long_open = None
    short_open = None

    # 遍历 spread 数据，判断开仓和关仓情况
    for i in range(200, len(spread)):
        current_spread = spread.iloc[i]
        mean_value = rolling_mean.iloc[i]
        std_value = rolling_std.iloc[i]
        current_date = aapl_data['Date'].iloc[i]

        # 判断是否开仓
        ##當預估值高於兩倍標準差，則開倉做short open，買進分母股票、賣出分子股票(這邊分別買進AAPL、賣出GLD)
        if current_spread > mean_value + 2 * std_value and not short_open:
            
            short_open = {
                'date': current_date, 
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_price': round(gld_data['Close'].iloc[i],2)
            }
            open_positions.append({'type': 'short', **short_open})
            profit_table.append({
                'type':'open',
                'date': current_date, 
                'appl_action' :'BUY',
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_action':'SELL',
                'gld_price': round(gld_data['Close'].iloc[i],2),
                'profit_percent': '-'
            })
            
            shares_aapl = 500 / aapl_data['Close'].iloc[i]
            shares_gld = 500 / gld_data['Close'].iloc[i]
        ##當預估值低於兩倍標準差時，則開倉做long open，賣出分母股票、買進分子股票(這邊分別買進GLD、賣AAPL)
        elif current_spread < mean_value - 2 * std_value and not long_open:
            
            long_open = {
                'date': current_date, 
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_price': round(gld_data['Close'].iloc[i],2)
            }
            open_positions.append({'type': 'long', **long_open})
            profit_table.append({
                'type':'open',
                'date': current_date, 
                'appl_action' :'SELL',
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_action':'BUY',
                'gld_price': round(gld_data['Close'].iloc[i],2),
                'profit_percent': '-'
            })
            shares_aapl = 500 / aapl_data['Close'].iloc[i]
            shares_gld = 500 / gld_data['Close'].iloc[i]
        if not short_open and not long_open:
            daily_profits.append({
                'date': current_date,
                'profit_percentage': (cumulative_profit)*100 / 1000
            })
        # 如果有开仓头寸，计算每日损益
        if short_open:                                  #(這邊分別買進AAPL、賣出GLD)
            
            profit =  (aapl_data['Close'].iloc[i] * shares_aapl) - (gld_data['Close'].iloc[i] * shares_gld)
            
            daily_profits.append({'date': current_date, 'profit_percent':  (cumulative_profit + profit)*100 / 1000})
        elif long_open:                                #(這邊分別買進GLD、賣AAPL)
            
            profit = - (aapl_data['Close'].iloc[i] * shares_aapl) + (gld_data['Close'].iloc[i] * shares_gld)
            
            daily_profits.append({'date': current_date, 'profit_percent':  (cumulative_profit + profit)*100 / 1000})

        # 判断是否关仓并计算最终损益
        if short_open and current_spread < mean_value:
            
            profit = (aapl_data['Close'].iloc[i] * shares_aapl) - (gld_data['Close'].iloc[i] * shares_gld)
            cumulative_profit += profit
            close_positions.append({
                'type': 'short', 
                'open': short_open, 
                'close': {
                    'date': current_date, 
                    'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                    'gld_price': round(gld_data['Close'].iloc[i],2)
                    #'profit_percent': cumulative_profit
                }
            })
            profit_table.append({
                'type':'close',
                'date': current_date, 
                'appl_action' :'SELL',
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_action':'BUY',
                'gld_price': round(gld_data['Close'].iloc[i],2),
                'profit_percent': cumulative_profit*0.1
            })
            short_open = None
        elif long_open and current_spread > mean_value:
            profit = -(aapl_data['Close'].iloc[i] * shares_aapl) + (gld_data['Close'].iloc[i] * shares_gld)
            cumulative_profit += profit
            close_positions.append({
                'type': 'long', 
                'open': long_open, 
                'close': {
                    'date': current_date, 
                    'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                    'gld_price': round(gld_data['Close'].iloc[i],2)
                    #'profit_percent': cumulative_profit
                }
            })
            profit_table.append({
                'type':'close',
                'date': current_date, 
                'appl_action' :'BUY',
                'aapl_price': round(aapl_data['Close'].iloc[i],2), 
                'gld_action':'SELL',
                'gld_price': round(gld_data['Close'].iloc[i],2),
                'profit_percent': cumulative_profit*0.1
            })
            long_open = None
   
    #print(close_positions)
    # 返回带有日期的 JSON 数据
    return JsonResponse({
        'AAPL': aapl_stock_data,
        'GLD': gld_stock_data,
        'spread': spread_with_date,
        'rolling_mean': rolling_mean_with_date,
        'rolling_std': rolling_std_with_date,
        'open_positions': open_positions,
        'close_positions': close_positions,
        'daily_profits': daily_profits,
        'profits':profit_table,
    }, safe=False)
    
    
def get_stock_data(request): 
    #print('start')
   
    # 下载股票数据
    aapl_data = yf.download('AAPL', start='2021-01-01', end='2024-01-01')
    gld_data = yf.download('GLD', start='2021-01-01', end='2024-01-01')
    
    # 保留日期信息并重置索引
    aapl_data = aapl_data[['Close']].reset_index()
    aapl_data['Date'] = aapl_data['Date'].dt.strftime('%Y-%m-%d')
    gld_data = gld_data[['Close']].reset_index()
    gld_data['Date'] = gld_data['Date'].dt.strftime('%Y-%m-%d')

    # 将数据转换为字典
    aapl_stock_data = aapl_data.to_dict(orient='records')
    gld_stock_data = gld_data.to_dict(orient='records')

    # 计算 spread、滚动均值和滚动标准差
    aapl_log_close = np.log(aapl_data['Close'])
    gld_log_close = np.log(gld_data['Close'])
    spread = gld_log_close - aapl_log_close
    rolling_mean = spread.rolling(window=200).mean()
    rolling_std = spread.rolling(window=200).std()

    # 填充 NaN 值
    rolling_mean_filled = rolling_mean.bfill()
    rolling_std_filled = rolling_std.bfill()

    # 将日期与计算结果结合，保留日期信息
    spread_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': spread[i]} for i in range(len(spread))]
    rolling_mean_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': rolling_mean_filled[i]} for i in range(len(rolling_mean_filled))]
    rolling_std_with_date = [{'date': aapl_data['Date'].iloc[i], 'value': rolling_std_filled[i]} for i in range(len(rolling_std_filled))]

    open_positions = []  # 记录开仓
    close_positions = []  # 记录关仓
    long_open = None
    short_open = None

    # 遍历 spread 数据，判断开仓和关仓情况
    for i in range(200, len(spread)):
        current_spread = spread.iloc[i]
        mean_value = rolling_mean.iloc[i]
        std_value = rolling_std.iloc[i]
        
        # 判断是否开仓
        if current_spread > mean_value + 2 * std_value and not short_open:
            # 开始做空
            short_open = {
                'date': aapl_data['Date'].iloc[i], 
                'aapl_price': aapl_data['Close'].iloc[i], 
                'gld_price': gld_data['Close'].iloc[i]
            }
            open_positions.append({'type': 'short', **short_open})
        elif current_spread < mean_value - 2 * std_value and not long_open:
            # 开始做多
            long_open = {
                'date': aapl_data['Date'].iloc[i], 
                'aapl_price': aapl_data['Close'].iloc[i], 
                'gld_price': gld_data['Close'].iloc[i]
            }
            open_positions.append({'type': 'long', **long_open})

        # 判断是否关仓
        if short_open and current_spread < mean_value:
            close_positions.append({
                'type': 'long', 
                'open': short_open, 
                'close': {
                    'date': aapl_data['Date'].iloc[i], 
                    'aapl_price': aapl_data['Close'].iloc[i], 
                    'gld_price': gld_data['Close'].iloc[i]
                }
            })
            short_open = None
        elif long_open and current_spread > mean_value:
            close_positions.append({
                'type': 'short', 
                'open': long_open, 
                'close': {
                    'date': aapl_data['Date'].iloc[i], 
                    'aapl_price': aapl_data['Close'].iloc[i], 
                    'gld_price': gld_data['Close'].iloc[i]
                }
            })
            long_open = None
    #print(open_positions)
    #print('====================================')
    #print(close_positions)
    # 返回带有日期的 JSON 数据
    return JsonResponse({
        'AAPL': aapl_stock_data,
        'GLD': gld_stock_data,
        'spread': spread_with_date,
        'rolling_mean': rolling_mean_with_date,
        'rolling_std': rolling_std_with_date,
        'open_positions': open_positions,
        'close_positions': close_positions
    }, safe=False)