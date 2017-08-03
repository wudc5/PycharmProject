#coding=utf-8
import psycopg2
import MySQLdb
import pandas as pd
from sqlalchemy import create_engine
import random

def getdataFromPG(sql, host, user, passwd, db):          # 得到PG中数据
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def getLabel(df, index, col, num1, num2, num3):          # 计算label
    if float(df.loc[index, col]) <= num1:
        lable = 0
    elif float(df.loc[index, col]) > num1 and float(df.loc[index, col]) <= num2:
        lable = 1
    elif float(df.loc[index, col]) > num2 and float(df.loc[index, col]) <= num3:
        lable = 2
    else:
        lable = 3
    return lable

def deletePGTable(table, host, user, passwd, db):          # 删除table
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    sql = "drop table {0}".format(table)
    cur.execute(sql)
    conn.close()

if __name__ == "__main__":
    # 初始化驱动
    mysql_engine = create_engine("mysql+mysqldb://root:123456@localhost:3306/lottery", echo=True)
    postgresql_engine = create_engine("postgresql://gpadmin:1qaz@WSX@192.168.199.152:5432/lottery", echo=True)
    # postgresql_engine = create_engine("postgresql://postgres:123456@localhost:5432/lottery", echo=True)

    # conn configure
    # conn_pg = psycopg2.connect(host="192.168.199.152", user="gpadmin", password="1qaz@WSX", database="lottery",
    #                            port='5432')
    conn_pg = psycopg2.connect(host="localhost", user="postgres", password="123456", database="lottery",
                               port='5432')
    conn_mysql = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="lottery", port=3306)

    # get data
    sql = "select account, age, gender, avgdailyvisit, avgdailyvisittime, ratioofvisitwith3page," \
          "avgdailyvisitsatworktime, avgdailyvisitsatofftime, avgdailymoney, " \
          "maxdailymoney, avgweekvisitsatofftime, avgbetmultiple, maxbetmultiple," \
          " avgweekbuycount from user_index limit 100000;"
    # dataList = GetDataFromPG(sql, "192.168.199.152", "gpadmin", "1qaz@WSX", "lottery")
    df = pd.read_sql(sql, conn_pg)             # pandas读取数据，返回DataFrame
    indexes = df.index
    cols = df.columns

    for col in cols:
        df[col] = df[col].fillna(0)

    divlineDic = {"avgdailyvisit": [2.1, 2.2, 2.3],
                  "avgdailyvisittime": [400, 450, 500],
                  "ratioofvisitwith3page": [0.13, 0.17, 0.21],
                  "avgdailyvisitsatworktime": [0.09, 0.12, 0.15],
                  "avgdailyvisitsatofftime": [0.27, 0.31, 0.37],
                  "avgdailymoney": [2300, 2900, 3400],
                  "avgweekvisitsatofftime": [1.4, 1.7, 2],
                  "maxdailymoney": [12000, 16000, 20000],
                  "avgbetmultiple": [32, 37, 40],
                  "maxbetmultiple": [98, 99, 99],
                  "avgweekbuycount": [7.8, 13, 14.5]
                  }

    for index in indexes:
        print "index: ", index
        labelList = []
        maxlabel = 0
        final_label = 0
        for key in divlineDic.keys():
            label = getLabel(df, index, key, divlineDic[key][0], divlineDic[key][1], divlineDic[key][2])
            labelList.append(label)
            final_label = labelList[random.randint(0, len(labelList)-1)]
            print "label: ", label
            # if maxlabel < label:
            #     maxlabel = label
        df.loc[index, 'label'] = final_label
        df.loc[index, 'id'] = index + 1

    # 设置字段类型
    for col in divlineDic.keys():
        df[[col]] = df[[col]].astype(float)
    df[["id"]] = df[["id"]].astype(int)

    print df
    try:
        deletePGTable("antiaddiction_train", "192.168.199.152", "gpadmin", "1qaz@WSX", "lottery")
        # deletePGTable("antiaddiction_train", "localhost", "postgres", "123456", "lottery")
    except Exception, e:
        print Exception, ":", e
    df.to_sql(name='antiaddiction_train', con=postgresql_engine, flavor=None, if_exists='append', index=False)