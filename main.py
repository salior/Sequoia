# -*- encoding: UTF-8 -*-

import utils
import logging
import work_flow
import settings
import schedule
import time
from pylab import mpl

def job():
    if utils.is_weekday():
        work_flow.prepare()


logging.basicConfig(format='%(asctime)s %(message)s', filename='sequoia.log')
logging.getLogger().setLevel(logging.INFO)
settings.init()

if settings.config['cron']:
    EXEC_TIME = "15:15"
    schedule.every().day.at(EXEC_TIME).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 指定默认字体：解决plot不能显示中文问题
    mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
    #work_flow.do_my_job()
    work_flow.prepare()
