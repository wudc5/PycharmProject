#coding=utf-8
import psycopg2
import pandas as pd
import numpy as np
import MySQLdb
import datetime
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima_model import ARIMA
import datetime, uuid
from sklearn import linear_model
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def getCurTime():
    now_time = datetime.datetime.now()
    return now_time.strftime('%Y-%m-%d')


def InsertToPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def GetDataFromPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def getDBdata(sql, host, user, passwd, db):
    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
    cur = conn.cursor()
    cur.execute('SET NAMES UTF8')
    conn.commit()
    oper = cur.execute(sql)
    data = cur.fetchmany(oper)
    cur.close()
    return data

def GetEndTime(stime, interval):
    stime = datetime.datetime.strptime(stime, '%Y-%m-%d')
    etime = stime + datetime.timedelta(days=+int(interval))
    return etime.strftime('%Y-%m-%d')


def ForecastByARIMA(data):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    data.plot()
    # plt.show()
    # plot_acf(data).show()
    print "data['销量']:", data['销量']
    # print data
    print '原始序列的ADF检验结果为：', ADF(data['销量'], 1)
    D_data = data.diff().dropna()
    print "D_data: ", D_data
    D_data.columns = [u'销量差分']
    D_data.plot()
    # plt.show()
    # plot_acf(D_data).show()

    # plt.show()
    # plot_pacf(D_data).show()
    # plt.show()
   # print('差分序列的ADF检验结果为：', ADF(D_data[u'销量差分'], 4))
    print'差分序列的白噪声检验结果为：', acorr_ljungbox(D_data, lags=1)
    pmax = int(len(D_data) / 10)
    qmax = int(len(D_data) / 10)

    print pmax, qmax
    bic_matrix = []
    data = np.array(data, dtype=np.float)
    for p in range(pmax + 1):
        print "p: ", p
        tmp = []
        for q in range(qmax + 1):
            print "q: ", q
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
    print "bic_matrix", bic_matrix
    # 先用stack展平，然后用idxmin找出最小值位置。
    p, q = bic_matrix.stack().idxmin()
    print('BIC最小的p值和q值为：%s、%s' % (p, q))

    model = ARIMA(data, (p, 1, q)).fit()

    # 给出一份模型报告

    # model.summary2()

    # 作为期1天的预测，返回预测结果、标准误差、置信区间。
    print "-->-->forecasting:   "
    return model.forecast(1)

def forecastByLinearModel(data):
        X_parameters = list()
        for i in range(1,4):
            X_parameters.append([i])
        print(X_parameters)
        Y_parameters = data['销量'].tolist()
        print("data:**********", data['销量'].tolist())
        # Create linear regression object
        regr = linear_model.LinearRegression()
        print "X_parameters", X_parameters
        regr.fit(X_parameters, Y_parameters)
        predict_outcome = regr.predict([[8]])
        return predict_outcome

def runJob(city, game, drawnum):    
#    city = sys.argv[1]
#    game = sys.argv[2]
#    drawnum = sys.argv[3]
    drawnum_1 = str(int(drawnum)-1)     
    drawnum_2 = str(int(drawnum)-2)     
    drawnum_3 = str(int(drawnum)-3)
    sql3 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gamename = '{1}' and saledrawnumber = '{2}'".format(city, game, drawnum_3)
    sql2 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gamename = '{1}' and saledrawnumber = '{2}'".format(city, game, drawnum_2)
    sql1 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gamename = '{1}' and saledrawnumber = '{2}'".format(city, game, drawnum_1)
    print "sql3: ", sql3
    saleamount3 = GetDataFromPG(sql3, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    saleamount2 = GetDataFromPG(sql2, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    saleamount1 = GetDataFromPG(sql1, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    if not saleamount1:
       saleamount1 = 4500 
    if not saleamount2:
       saleamount2 = 4600
    if not saleamount3:
       saleamount3 = 4700
    print saleamount1, saleamount2, saleamount3

    drawnumlist = list()
    amountlist = list()
    drawnumlist.append(drawnum_1)
    drawnumlist.append(drawnum_2)
    drawnumlist.append(drawnum_3)
    amountlist.append(int(saleamount1))
    amountlist.append(int(saleamount2))
    amountlist.append(int(saleamount3))
    amountmap = {'销量': amountlist}
    data = pd.DataFrame(amountmap, index=drawnumlist)
    print data
    data = data.astype(float)

    # 线性回归预测
    # f_value = round(forecastByLinearModel(data)[0], 2)

    # arima预测
    f_value = round(ForecastByARIMA(data)[0][0], 2)
    print "f_value: ", f_value      #forecast value
    
    # get true sale amount
    sql4 = "select sum(drawsaleamount) as saleamount from drawsalegrandtotal where cityname = '{0}' and gamename = '{1}' and saledrawnumber = '{2}'".format(city, game, drawnum)
    truesaleamount = GetDataFromPG(sql4, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    print "truesaleamount: ", truesaleamount

    # get provinceid
    sql5 = "select provinceid, provincename from drawsalegrandtotal where cityname = '{0}'".format(city)
    print "sql5: ", sql5
    provinceinfo = GetDataFromPG(sql5, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
    provinceid = provinceinfo[0][0]
    provincename = provinceinfo[0][1]
    sql6 = "select cityid from drawsalegrandtotal where cityname = '{0}'".format(city)
    print "sql6: ", sql6
    sql7 = "select gameid from drawsalegrandtotal where gamename = '{0}'".format(game)
    print "sql7: ", sql7
    gameid = GetDataFromPG(sql6, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    cityid = GetDataFromPG(sql7, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')[0][0]
    sql_insert = "insert into saleforecast_test({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7},{8}, {9},{10},{11}) values('{12}','{13}','{14}','{15}','{16}','{17}', '{18}', '{19}', '{20}', '{21}','{22}','{23}')".format('"uuid"','"drawnum"','"preds_time"','"provincename"', '"provinceid"', '"cityname"', '"cityid"','"gamename"','"gameid"','"period"','"forecast_amount"', '"true_amount"', str(uuid.uuid1()).replace("-",""), drawnum, getCurTime(), provincename, provinceid, city, cityid, game, gameid, "draw", f_value, truesaleamount)
    print 'sql_insert: ', sql_insert
    InsertToPG(sql_insert, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')



if __name__ == '__main__':
    gamelist = ['双色球','七乐彩']
    sql_city = "select distinct(cityname) from drawsalegrandtotal"
    citylist = GetDataFromPG(sql_city, '192.168.199.152', 'gpadmin', '1qaz@WSX', 'lottery')
    drawnumlist = ['2017053', '2017054', '2017055']
    for city in citylist:
        if city[0]:
            for game in gamelist:
                for drawnum in drawnumlist:
                    print "city：", city[0]
                    print "game：", game
                    print "drawnum：", drawnum
                    runJob(city[0], game, drawnum)
