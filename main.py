import requests
import pymysql
import utils.log

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from bs4 import BeautifulSoup
from datetime import datetime


logger = utils.log.gen_logger('ncu_100 on duty', 'duty.log')

job_stores = {
    "default": MemoryJobStore()
}

executors = {
    "default": ThreadPoolExecutor(4)
}

scheduler = BlockingScheduler()


def get_html(url):

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cookie': 'JSESSIONID=8398B8675BDF1BB115565704078660BD'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text.encode("utf8").decode()


def get_count():
    html = get_html(url="http://giving.ncu.edu.cn/project.action?id=10621")

    soup = BeautifulSoup(html, "html.parser")
    count = soup.select(".progressInfoLeft>b")[1].text[1:].replace(',', "")
    return count


def get_detail():
    html = get_html(url="http://giving.ncu.edu.cn/project!orderList.action?proj=10621")
    soup = BeautifulSoup(html, "html.parser")
    data = []
    detail_list = soup.select("table >tr")
    for detail in detail_list[1:]:
        data.append([i.text.replace("\r", "").replace("\t", "").replace("\n", "") for i in detail.select("td")])

    return data


class DB:
    def __init__(self):
        self.db = pymysql.connect()

    def update_count(self):
        count = get_count()
        time_ = datetime.now()
        sql = """insert into  giving_count (time_ , amount) values (%s, %s)"""
        self.db.cursor().execute(sql, [time_, count])
        self.db.commit()
        logger.critical("insert count   " + count + "   done")

    def update_detail(self):

        details = get_detail()

        get_sql = """ select name ,giving_select, amount from giving_detail order by datetime_ desc limit 24"""
        cur = self.db.cursor()
        r = cur.execute(get_sql)
        results = cur.fetchall()

        inter = [i for i in details if (i[0], i[1], i[2]) not in results]
        update_sql = """insert into  giving_detail (name ,giving_select, amount,datetime_) values (%s, %s,%s,%s)"""
        self.db.cursor().executemany(update_sql, inter)
        self.db.commit()
        logger.critical("insert detail done")


if __name__ == '__main__':
    a = DB()
    scheduler.configure(jobstores=job_stores, executors=executors, timezone=timezone("Asia/Shanghai"))
    scheduler.add_job(a.update_count, "cron", hour=0, minute=0, second=0)
    scheduler.add_job(a.update_count, "cron", hour=6, minute=0, second=0)
    scheduler.add_job(a.update_count, "cron", hour=12, minute=0, second=0)
    scheduler.add_job(a.update_count, "cron", hour=18, minute=0, second=0)
    scheduler.add_job(a.update_detail, "interval", minutes=1)
    scheduler.start()
