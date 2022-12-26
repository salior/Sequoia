# -*- encoding: UTF-8 -*-
import logging
import settings

# 回手掏战法
def check(code_name, data, rec_df, end_date=None, threshold=60):
    # 龙虎榜上必须有机构
    # if code_name[0] not in settings.top_list:
    #     return False

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold)

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
            #print(str(code_name) + ' 在 ' + data.iloc[i]['日期'] + ' 5日内产生' + "%.2f" % per + "%的涨幅")
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
                    low_last_day = 0 #创低点的时间
                    for j in range(k,len(data)):#向后找到回落低点，判断条件为5日内没有新低产生，并且当前价格已从低点反弹10%
                        if data.iloc[j]['最低'] < low_p:
                            low_p = data.iloc[j]['最低']
                            low_day = data.iloc[j]['日期']
                            low_last_day = j - k + 4

                        if data.iloc[j]['收盘'] > low_p:
                            last_day += 1
                        else:
                            last_day = 0
                        if last_day > 4 and 100*(data.iloc[j]['收盘'] - low_p)/low_p >= 10:
                            in_level = 3
                            print(str(code_name) + ' 在 ' + low_day + ' 达到回撤低点 ' + str(low_p) + ',最高撤幅 ' + "%.2f"%(100*(high_p - low_p)/high_p))
                            i = j

                            high2_p = low_p #反弹高点
                            last_day = 0 #持续时间
                            rebound_last_day = 0 #反弹的时间
                            for m in range(j,len(data)):#向后找到反弹高点，判断条件为5日内没有新高产生，并且当前价格已从高点回落10%
                                if data.iloc[m]['最高'] > high2_p:
                                    high2_p = data.iloc[m]['最高']
                                    high2_day = data.iloc[m]['日期']
                                    high2_last_day = m - j + 4

                                if data.iloc[m]['收盘'] < high2_p:
                                    last_day += 1
                                else:
                                    last_day = 0
                                if last_day > 4 and 100*(high2_p - data.iloc[m]['收盘'])/high2_p >= 10:
                                    in_level = 0 #进到这里就不用标记打印了
                                    if high2_p > high_p:
                                        print(str(code_name) + ' 在 ' + high2_day + ' 达到反转高点 ' + str(high2_p) + ',最高反转涨幅 ' + "%.2f"%(100*(high2_p - low_p)/low_p))
                                    else:
                                        print(str(code_name) + ' 在 ' + high2_day + ' 达到反弹高点 ' + str(high2_p) + ',最高反弹涨幅 ' + "%.2f"%(100*(high2_p - low_p)/low_p))
                                    i = m
                                    #['号码','股票名','起始日期','起始价格','高点日期','高点价格','高点涨幅','起时间','低点日期','低点价格','回撤跌幅','落时间','反弹结束','反弹价格','反弹幅度','反弹时间','是否反转','持续时间']
                                    rec_df.loc[len(rec_df)]=[str(code_name[0]),code_name[1],begin_day,begin_p,high_day,high_p,round(100*(high_p-begin_p)/begin_p,1),high_last_day,\
                                            low_day,low_p,round(100*(high_p - low_p)/high_p,1),low_last_day,high2_day,high2_p,round(100*(high2_p - low_p)/low_p,1),\
                                            high2_last_day,high2_p > high_p,high_last_day+low_last_day+high2_last_day]
                                    break
                                #else:
                                #    print(str(code_name) + ' 在 ' + high2_day + "后没有找到反弹高点") #这个一般不应该出现，除非在最近找出来的还未达到高点
                            break
                        # else:
                        #     print(str(code_name) + ' 在 ' + low_day + "后没有找到回撤低点") #这个一般不应该出现，除非在最近找出来的还未达到低点
                    break
                # else:
                #     print(str(code_name) + ' 在 ' + high_day + "之后没有找到上升高点") #这个一般不应该出现，除非在最近找出来的还未达到高点的股
        if in_level > 0:
            print(str(code_name) + ' 在 ' + data.iloc[i]['日期'] + "之后进入了条件 " + str(in_level)) #这个一般不应该出现，除非在最近找出来的股还没走完全程
        i += 1
        

    return False
