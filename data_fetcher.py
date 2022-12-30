# -*- encoding: UTF-8 -*-

import akshare as ak
import logging
import talib as tl
import os
import concurrent.futures
import pandas as pd

def fetch(code_name,data_dir):
    stock = code_name[0]

    save_file = os.path.join(data_dir, stock+'.csv')

    if os.path.exists(save_file):
        print("restore file:" + save_file)
        return pd.read_csv(save_file,encoding='utf-8-sig')
    else:
        data = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date="20200101", adjust="qfq")

        if data is None or data.empty:
            logging.debug("股票："+stock+" 没有数据，略过...")
            return

        data['p_change'] = tl.ROC(data['收盘'], 1)

        print("now save file:" + save_file)
        data.to_csv(save_file,encoding='utf-8-sig')
        return data


def run(stocks):
    data_dir = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
    data_dir = data_dir + '\\stockData'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    #取到的数据如下：p_charge是代码自己加的，等同于涨幅
    #Index(['Unnamed: 0', '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅','涨跌额','换手率’,'p_charge']}
    stocks_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_stock = {executor.submit(fetch, stock, data_dir): stock for stock in stocks}
        for future in concurrent.futures.as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                data = future.result()
                if data is not None:
                    data = data.astype({'成交量': 'double'})
                    stocks_data[stock] = data
            except Exception as exc:
                print('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))

    return stocks_data
