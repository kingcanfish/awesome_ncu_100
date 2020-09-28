FROM python:3.6
MAINTAINER kingcanfish <tgxylong@126.com>

RUN pip install apscheduler pymysql requests beautifulsoup4 --no-cache-dir -i https://pypi.douban.com/simple

WORKDIR /code

CMD ["python", "main.py"]