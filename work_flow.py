# -*- encoding: UTF-8 -*-

import data_fetcher
import settings
import utils
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
import akshare as ak
import push
import logging
import time
import datetime
import pandas as pd
from strategy import high_go_back
import matplotlib.pyplot as plt
from backtest import high_go_backtest1

import numpy as np
import seaborn as sns

def sns_plot(df_data,data_name,bjust_print=True):
    ax = sns.kdeplot(df_data[data_name])
    x = ax.lines[0].get_xdata() # Get the x data of the distribution
    y = ax.lines[0].get_ydata() # Get the y data of the distribution
    maxid = np.argmax(y) # The id of the peak (maximum of y data)
    if bjust_print:
        print("data_name 大概率值为 %.1f%%"%(x[maxid]))
    else:
        plt.plot(x[maxid],y[maxid], 'bo', ms=3)
        plt.text(x[maxid],y[maxid],"%.1f"%(x[maxid]))
        plt.show()
    return x[maxid]

def do_analyse(df_data):
    #画高点涨幅的正态分布图
    print("最高涨幅标准差为：%.2f%%,平均值：%.2f%%,"%(df_data['高点涨幅'].std(),df_data['高点涨幅'].mean()))
    print("回撤跌幅标准差为：%.2f%%,平均值：%.2f%%,"%(df_data['回撤跌幅'].std(),df_data['回撤跌幅'].mean()))
    print("反弹幅度标准差为：%.2f%%,平均值：%.2f%%,"%(df_data['反弹幅度'].std(),df_data['反弹幅度'].mean()))
    # 这个是用DataFrame的画图函数出来的，拿不到点
    # df_data['高点涨幅'].plot(kind="kde",title="高点涨幅")
    # plt.show()
    # df_data['回撤跌幅'].plot(kind="kde",title="回撤跌幅")
    # plt.show()
    # df_data['反弹幅度'].plot(kind="kde",title="反弹幅度")
    # plt.show()

    #用sns
    h = sns_plot(df_data,'高点涨幅')
    b = sns_plot(df_data,'回撤跌幅')
    r = sns_plot(df_data,'反弹幅度')

    return h,b,r

def do_my_job(bdo_analyse = True):
    logging.info("************************ Cy job start ***************************************")
    all_data = ak.stock_zh_a_spot_em()
    subset = all_data[['代码', '名称']]
    stocks = [tuple(x) for x in subset.values]
    statistics(all_data, stocks)

    #stocks_data = data_fetcher.run(stocks)
    stocks_data = data_fetcher.run(stocks[0:100])#调试只用100个股票数据就好了

    end_date = settings.config['end_date']
    df= pd.DataFrame(columns=['号码','股票名','起始日期','起始价格','高点日期','高点价格','高点涨幅','起时间','低点日期','低点价格','回撤跌幅','落时间','反弹结束','反弹价格','反弹幅度','反弹时间','是否反转','持续时间']) 
    for stock_data in stocks_data.items():
        high_go_back.check(stock_data[0], stock_data[1], df,end_date=end_date,threshold=len(stock_data[1]))

    df.to_csv('filterData.csv',encoding='utf-8-sig')

    h = 0.537
    b = 0.236
    r = 0.231
    if bdo_analyse:
        h,b,r = do_analyse(df)
    
    print("现在以 高幅%.1f%%,撤幅%.1f%%,弹幅%.1f%% 为参数回测最近一年数据"%(h,b,r))

    logging.info("************************ Cy job end   ***************************************")

def go_test():
    logging.info("************************ Cy test start ***************************************")
    all_data = ak.stock_zh_a_spot_em()
    subset = all_data[['代码', '名称']]
    stocks = [tuple(x) for x in subset.values]
    #stocks_data = data_fetcher.run(stocks)
    stocks_data = data_fetcher.run(stocks[0:100])#调试只用100个股票数据就好了

    end_date = settings.config['end_date']
    high_go_backtest1.do_h2h_backtest(stocks_data)

    logging.info("************************ Cy test end   ***************************************")
    pass

def prepare():
    logging.info("************************ process start ***************************************")
    all_data = ak.stock_zh_a_spot_em()
    subset = all_data[['代码', '名称']]
    stocks = [tuple(x) for x in subset.values]
    statistics(all_data, stocks)

    strategies = {
        '放量上涨': enter.check_volume,
        '均线多头': keep_increasing.check,
        '停机坪': parking_apron.check,
        '回踩年线': backtrace_ma250.check,
        # '突破平台': breakthrough_platform.check,
        '无大幅回撤': low_backtrace_increase.check,
        '海龟交易法则': turtle_trade.check_enter,
        '高而窄的旗形': high_tight_flag.check,
        '放量跌停': climax_limitdown.check,
    }

    if datetime.datetime.now().weekday() == 0:
        strategies['均线多头'] = keep_increasing.check

    process(stocks, strategies)


    logging.info("************************ process   end ***************************************")

def process(stocks, strategies):
    #stocks_data = data_fetcher.run(stocks)
    stocks_data = data_fetcher.run(stocks[0:100])#调试只用100个股票数据就好了
    for strategy, strategy_func in strategies.items():
        check(stocks_data, strategy, strategy_func)
        time.sleep(2)

def check(stocks_data, strategy, strategy_func):
    end = settings.config['end_date']
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = dict(filter(m_filter, stocks_data.items()))
    if len(results) > 0:
        push.strategy('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)


    return end_date_filter


# 统计数据
def statistics(all_data, stocks):
    limitup = len(all_data.loc[(all_data['涨跌幅'] >= 9.5)])
    limitdown = len(all_data.loc[(all_data['涨跌幅'] <= -9.5)])

    up5 = len(all_data.loc[(all_data['涨跌幅'] >= 5)])
    down5 = len(all_data.loc[(all_data['涨跌幅'] <= -5)])

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}".format(limitup, limitdown, up5, down5)
    push.statistics(msg)


