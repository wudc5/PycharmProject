#coding=utf-8
import os
import datetime

time1 = datetime.datetime.strptime('2009-01-01', '%Y-%m-%d')
endtime = datetime.datetime.strptime('2009-12-24', '%Y-%m-%d')
while time1 <= endtime:
      stime = time1.strftime('%Y-%m-%d')
      os.popen('python /home/hadoop/pythoncode/salesForecast.py {0}2009-01-01 7 北京市 双色球'.format(stime))
      time1 = time1 + datetime.timedelta(days=+int(1))
