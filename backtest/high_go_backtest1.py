# -*- encoding: UTF-8 -*-
import logging
import settings

#高点前杀入策略,符合5日涨幅超30%的条件后，在当天收盘竞价杀入，在后面伺机卖出（待确定卖出条件）
def do_h2h_backtest(data, start_date=None, end_date=None):
    # 龙虎榜上必须有机构
    # if code_name[0] not in settings.top_list:
    #     return False
    if start_date is None:
        start_date = data.iloc[0]['日期']

    if end_date is None:
        end_date = data.iloc[len(data)-1]['日期']

    mask = (data['日期'] <= end_date) and  (data['日期'] >= start_date)
    data = data.loc[mask]

    if len(data) < 60:
        #logging.debug("{0}:样本小于{1}天,不处理...\n".format(code_name, 60))
        print("{0}:样本小于{1}天,不处理...\n".format(code_name, 60))
        return False

    # 5天内涨幅大于等于30%
    i = 4
    length = len(data)
    while i < length:
        # 已经进入的条件层数,用来观察进入筛选条件后有没有符合后面的条件
        in_level = 0
        per = 100*(data.iloc[i]['收盘'] - data.iloc[i - 4]['收盘'])/data.iloc[i - 4]['收盘']
        if  per >= 30:#第一条件，5日升幅超30%
            in_level = 1
            print(str(code_name) + ': 在 ' + data.iloc[i]['日期'] + ' 收盘前以收盘价 ' + "%.2f"%data.iloc[i]['收盘'] + "买入")
            high_p = 0
            last_day = 0 #持续时间
            begin_day = data.iloc[i - 4]['日期']
            begin_p = data.iloc[i - 4]['收盘']
            high_last_day = 0 #创高点的时间

            high_day = data.iloc[i]['日期']
            for k in range(i,len(data)):#向后找到高点，判断条件为5日内没有新高产生，并且当前价格已从高点回落10%
                if data.iloc[k]['最高'] > high_p:
                    high_p = data.iloc[k]['最高']
                    high_day = data.iloc[k]['日期']
                    high_last_day = k - i + 4

                if data.iloc[k]['收盘'] < high_p:
                    last_day += 1
                else:
                    last_day = 0
                if last_day > 4 and 100*(high_p - data.iloc[k]['收盘'])/high_p >= 10:
                    in_level = 2
                    print(str(code_name) + ' 在 ' + high_day + ' 达到高点 ' + str(high_p) + ',最高涨幅 ' + "%.2f"%(100*(high_p - begin_p)/begin_p))
                    low_p = high_p
                    low_day = data.iloc[k]['日期']
                    last_day = 0 #持续时间
                    i = k
               
 
                    break
                # else:
                #     print(str(code_name) + ' 在 ' + high_day + "之后没有找到上升高点") #这个一般不应该出现，除非在最近找出来的还未达到高点的股
        if in_level > 0:
            print(str(code_name) + ' 在 ' + data.iloc[i]['日期'] + "之后进入了条件 " + str(in_level)) #这个一般不应该出现，除非在最近找出来的股还没走完全程
        i += 1
        
    return False
