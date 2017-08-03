#coding=utf-8
import psycopg2
import pandas as pd
import numpy as np
# import MySQLdb
import datetime
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima_model import ARIMA
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def getSaleAmount(city, gameid):
    sql_avggameamount = "select avg(amount) as avggameamount from (select sum(drawsaleamount) as amount, saledrawnumber from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' GROUP BY saledrawnumber) a".format(city, gameid)
    avggameamount = GetDataFromPG(sql_avggameamount, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
    print "avggameamount: ", avggameamount[0][0]
    if avggameamount == None:
        sql_avgcityamount = "select avg(amount) as avgcityamount from (select sum(drawsaleamount) as amount, gamename,saledrawnumber from drawsalegrandtotal where cityname = '{0}' group by saledrawnumber, gamename) a".format(city)
        avgcityamount = GetDataFromPG(sql_avgcityamount, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
        print "avgcityamount: ", avgcityamount
        return avgcityamount[0][0]
    else:
        return avggameamount[0][0]

def InsertToPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def GetDataFromPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    # cur.execute("SET CLIENT_ENCODING TO 'LATIN1';")
    cur.execute(sql)
    data = cur.fetchall()
    return data

# def getDBdata(sql, host, user, passwd, db):
#     conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
#     cur = conn.cursor()
#     cur.execute('SET NAMES UTF8')
#     conn.commit()
#     oper = cur.execute(sql)
#     data = cur.fetchmany(oper)
#     cur.close()
#     return data

def GetEndTime(stime, interval):
    stime = datetime.datetime.strptime(stime, '%Y-%m-%d')
    etime = stime + datetime.timedelta(days=+int(interval))
    return etime.strftime('%Y-%m-%d')


def ForecastByARIMA(data):
    print "data: ", data
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # data.plot()
    # plt.show()
    # plot_acf(data).show()
    # print data
    print '原始序列的ADF检验结果为：', ADF(data['销量'], 1)
    D_data = data.diff().dropna()
    D_data.columns = [u'销量差分']
    # D_data.plot()
    # plt.show()
    # plot_acf(D_data).show()

    # plt.show()
    # plot_pacf(D_data).show()
    # plt.show()
    print('差分序列的ADF检验结果为：', ADF(D_data[u'销量差分'], 1))
    print'差分序列的白噪声检验结果为：', acorr_ljungbox(D_data, lags=1)
    pmax = int(len(D_data) / 10)
    qmax = int(len(D_data) / 10)
    print pmax, qmax
    bic_matrix = []
    data = np.array(data, dtype=np.float)
    for p in range(pmax + 1):
        tmp = []
        for q in range(qmax + 1):
            # 存在部分报错，所以用try来跳过报错。
            try:
                print "************:", ARIMA(data, (p, 1, q)).fit().bic, "&&&&&&&&&&"
                tmp.append(ARIMA(data, (p, 1, q)).fit().bic)
            except:
                print "&&&&&&&&&&&&&&&&error"
                tmp.append(None)
        bic_matrix.append(tmp)
    # 从中可以找出最小值
    bic_matrix = pd.DataFrame(bic_matrix)
    print "bic_matrix: \n", bic_matrix

    # 先用stack展平，然后用idxmin找出最小值位置。
    p, q = bic_matrix.stack().idxmin()
    print('BIC最小的p值和q值为：%s、%s' % (p, q))

    model = ARIMA(data, (p, 1, q)).fit()

    # 给出一份模型报告

    # model.summary2()

    # 作为期5天的预测，返回预测结果、标准误差、置信区间。
    print "-->-->forecasting:   "
    return model.forecast(1)


if __name__ == '__main__':

    # print "action."
    #
    # stime = '2017-05-13'
    # interval = 7
    # city = '兰州市'
    # game = '双色球'
    # etime = GetEndTime(stime, interval)
    # print stime, etime, city, game
    #
    # # sql = "select {0}, AVG(cast(sales_forecast_2009.{1} as integer)) from sales_forecast_2009 where {2} = '{3}' and {4} = '{5}' and {6} >= '{7}' and {8} < '{9}' GROUP BY {10} ORDER BY {11}".format('"Date"', '"Sales"', '"City"', city, '"Game"', game, '"Date"', stime, '"Date"', etime, '"Date"', '"Date"')
    # # sql = "select {0}, AVG(cast(sales_forecast_2009.{1} as integer)) from daysalegrandtotal where {2} = '{3}' and {4} = '{5}' and {6} >= '{7}' and {8} < '{9}' ORDER BY {10}".format('"Date"', '"Sales"', '"City"', city, '"Game"', game, '"Date"', stime, '"Date"', etime, '"Date"')
    # sql = "select saletime, daysaleamount from daysalegrandtotal where saletime >= '{0}' and saletime <= '{1}' and cityname = '{2}' and gamename = '{3}' ORDER BY saletime;".format(stime, etime, city, game)
    # print sql
    # # sql = "select * from daysalegrandtotal limit 10"
    # datalist = GetDataFromPG(sql, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
    # print "datalist: ", datalist
    # print type(datalist[0])
    # print datalist
    # date = list()
    # sales = list()
    # for data in datalist:
    #     date.append(pd.to_datetime(data[0]))
    #     sales.append(int(data[1]))
    # data = {'销量': sales}
    # data = {'销量': [4500.0, 4700.0, 4800.0, 4670.0, 4590.0, 4590.0, 4870.0]}
    # data = {'销量': [2.00, 2.00, 2.00, 2.00, 2.00, 2.00, 2.00, 2.10, 2.00, 2.00]}
    # data = pd.DataFrame(data, index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # print type(data.index[0])
    # print "data: ", data
    # data = data.astype(float)
    # data.plot()
    # # plt.show()
    #
    # f_value = ForecastByARIMA(data)
    # print "*************{0}".format(int(f_value[0][0]))
    # sql2 = "select {0}, cast(AVG(cast(sales_forecast_2009.{1} as integer)) as integer) from sales_forecast_2009 where {2} = '{3}' and {4} = '{5}' and {6} = '{7}' GROUP BY {8} ORDER BY {9}".format('"Date"', '"Sales"', '"City"', city, '"Game"', game, '"Date"', etime, '"Date"', '"Date"')
    # data2 = GetDataFromPG(sql2, '192.168.199.152', 'cwlgp', 'cwl12345', 'lottery')
    # print data2[0][1]
    # sql_insert = "insert into arima_forecast({0}, {1}, {2}) values('{3}',{4},{5})".format('"date"', '"forecast_value"', '"true_value"', etime, int(f_value[0][0]), int(data2[0][1]))
    # # InsertToPG(sql_insert, '192.168.199.152', 'cwlgp', 'cwl12345', 'lottery')
    # print sql_insert

    gameMap = {"10001": "双色球", "10003": "七乐彩"}
    gameidlist = gameMap.keys()
    drawnumlist = [2017057, 2017058, 2017059, 2017060, 2017061, 2017062, 2017063, 2017064, 2017065, 2017066]
    sql_citylist = "select distinct(cityname) as cityname from drawsalegrandtotal"
    citylist = GetDataFromPG(sql_citylist, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
    for city in citylist:
        print city[0]
        if city[0] != None:
            for gameid in gameidlist:
                for drawnum in drawnumlist:
                    drawnum1 = (drawnum - 1)
                    drawnum2 = (drawnum - 2)
                    drawnum3 = (drawnum - 3)
                    drawnum4 = (drawnum - 4)
                    drawnum5 = (drawnum - 5)
                    drawnum6 = (drawnum - 6)
                    drawnum7 = (drawnum - 7)
                    drawnum8 = (drawnum - 8)
                    drawnum9 = (drawnum - 9)
                    drawnum10 = (drawnum - 10)
                    sql1 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum1)
                    sql2 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum2)
                    sql3 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum3)
                    sql4 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum4)
                    sql5 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum5)
                    sql6 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum6)
                    sql7 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum7)
                    sql8 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum8)
                    sql9 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum9)
                    sql10 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum10)

                    saleamount1_tmp = GetDataFromPG(sql1, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount2_tmp = GetDataFromPG(sql2, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount3_tmp = GetDataFromPG(sql3, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount4_tmp = GetDataFromPG(sql4, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount5_tmp = GetDataFromPG(sql5, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount6_tmp = GetDataFromPG(sql6, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount7_tmp = GetDataFromPG(sql7, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount8_tmp = GetDataFromPG(sql8, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount9_tmp = GetDataFromPG(sql9, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    saleamount10_tmp = GetDataFromPG(sql10, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    print "saleamount1_tmp: ", saleamount1_tmp
                    if saleamount1_tmp == None:
                        saleamount1 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount1 = saleamount1_tmp

                    if saleamount2_tmp == None:
                        saleamount2 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount2 = saleamount2_tmp

                    if saleamount3_tmp == None:
                        saleamount3 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount3 = saleamount3_tmp

                    if saleamount4_tmp == None:
                        saleamount4 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount4 = saleamount4_tmp
                    if saleamount5_tmp == None:
                        saleamount5 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount5 = saleamount5_tmp

                    if saleamount6_tmp == None:
                        saleamount6 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount6 = saleamount6_tmp
                    if saleamount7_tmp == None:
                        saleamount7 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount7 = saleamount7_tmp

                    if saleamount8_tmp == None:
                        saleamount8 = float(getSaleAmount(city[0], gameid)) + 0.01
                    else:
                        saleamount8 = float(saleamount8_tmp) + 0.01

                    if saleamount9_tmp == None:
                        saleamount9 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount9 = saleamount9_tmp

                    if saleamount10_tmp == None:
                        saleamount10 = getSaleAmount(city[0], gameid)
                    else:
                        saleamount10 = saleamount10_tmp

                    print "saleamount1: ", saleamount1
                    print "saleamount2: ", saleamount2
                    print "saleamount3: ", saleamount3
                    print "saleamount4: ", saleamount4
                    print "saleamount5: ", saleamount5
                    print "saleamount6: ", saleamount6
                    print "saleamount7: ", saleamount7
                    print "saleamount8: ", saleamount8
                    print "saleamount9: ", saleamount9
                    print "saleamount10: ", saleamount10
                    saleamountlist = [saleamount1, saleamount2, saleamount3, saleamount4, saleamount5, saleamount6, saleamount7, saleamount8, saleamount9, saleamount10]
                    data = {'销量': saleamountlist}
                    data = pd.DataFrame(data, index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                    data = data.astype(float)

                    print "arima 预测中...."
                    f_value = ForecastByARIMA(data)[0][0]
                    print "f_value: ", f_value

                    # get true value
                    sql11 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gameid = '{1}' and saledrawnumber = '{2}'".format(city[0], gameid, drawnum)
                    true_amount = GetDataFromPG(sql11, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
                    if true_amount == None:
                        true_amount = 0
                    print "true_amount: ", true_amount

                    # save
                    sql12 = "insert into saleforecast_arima({0}, {1}, {2}, {3}, {4}, {5}) values('{6}', '{7}', '{8}', '{9}', '{10}', '{11}')".format('"lotterynum"', '"cityname"', '"gamename"', '"gameid"', '"forecast_amount"', '"true_amount"', drawnum, city[0], gameMap[gameid], gameid, f_value, true_amount)
                    print "sql12: ", sql12
                    InsertToPG(sql12, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')









