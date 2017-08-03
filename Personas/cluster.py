#coding=utf-8
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans
import psycopg2
import MySQLdb
import pandas as pd
import numpy
from sklearn import preprocessing
import csv
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def SaveToCSV(content, k):
    csvfile = file('centers\centers_{0}.csv'.format(k), 'ab')
    writer = csv.writer(csvfile)
    writer.writerow(content)

def SaveToFile(row):
    with open('./centers\\true_center.txt', 'a') as wp:
        wp.write(row + "\n")
        wp.close()

def OneHotEncode(df, sql, col):
    onehot_encoder = DictVectorizer()
    kindlist = GetDataFromPG(sql, '192.168.199.152', 'cwlgp', 'cwl12345', 'lottery') 
    kindmaplist = list()
    for kind in kindlist:
        kindmaplist.append({col: kind[0]})
    kindcode = onehot_encoder.fit_transform(kindmaplist).toarray()

    kind_dic = dict()
    for i in range(len(kindlist)):
        kind_dic[kindlist[i][0]] = kindcode[i] 
        print kindcode[i]
    for i in range(len(df[col])):
        df[col][i] = kind_dic[df[col][i]]
        print df[col][i]
    return df

def kmeansCluster(features, k):
    # k-means 聚类
    clf = KMeans(n_clusters=int(k))
    s = clf.fit(features)
    centers = clf.cluster_centers_
    labels = clf.labels_
    print "centers: ", centers
    print "labels: ", labels
    return centers, labels

def pcaProcess(features_minmax, weidu):
    pca = PCA(n_components=int(weidu))
    pca.fit(features_minmax)
    features_new = pca.transform(features_minmax)  # 处理成二维特征
    return features_new, pca

def minmaxScale(features):
    min_max_scaler = preprocessing.MinMaxScaler()
    features_minmax = min_max_scaler.fit_transform(features)
    print "after minmax process: ", features_minmax
    return features_minmax

def GetDataFromPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def getDataFromDB(sql, host, user, passwd, db):
    conn = MySQLdb.connect(host=host, user=user, password=passwd, database=db, charset='utf-8')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def showCluster(dataSet, k, centroids, clusterAssment, totalnum):
        k = int(k)
        numSamples, dim = dataSet.shape
        if dim != 2:
            print "Sorry! I can not draw because the dimension of your data is not 2!"
            return 1
        mark = ['or', 'ob', 'og', 'ok', '^r', '+r', 'sr', 'dr', '<r', 'pr']
        if k > len(mark):
            print "Sorry! Your k is too large! please contact Zouxy"
            return 1

        # draw all samples
        for i in xrange(numSamples):
            markIndex = int(clusterAssment[i])
            plt.plot(dataSet[i, 0], dataSet[i, 1], mark[markIndex])

        mark = ['Dr', 'Db', 'Dg', 'Dk', '^b', '+b', 'sb', 'db', '<b', 'pb']

        # draw the centroids
        for i in range(k):
            plt.plot(centroids[i, 0], centroids[i, 1], mark[i], markersize=12)
        plt.savefig('./picture/{0}_centers_{1}.png'.format(totalnum, k))
        plt.show()

def numericalTime(df, col):
    for i in range(len(df[col])):
        hour = int(df[col][i][:2])
        if hour >= 0 and hour < 8:
            df[col][i] = [1, 0, 0]
        elif hour >= 8 and hour <16:
            df[col][i] = [0, 1, 0]
        else:
            df[col][i] = [0, 0, 1]
    return df


if __name__ == '__main__':
    print 'start..'
    totalnum = sys.argv[1]
    k = sys.argv[2]
    print "******************", totalnum, k
    sql = "select * from personas order by id limit {0}".format(totalnum)
    sql_job = "select job from personas group by job"
    sql_address = "select address from personas group by address"
    sql_edu = "select education from personas group by education"
    sql_pay = "select payment from personas group by payment"
    sql_risk = "select risk from personas group by risk"
    sql_repu = "select reputation from personas group by reputation"
    sql_gameid = "select game_id from personas group by game_id"

    #get data
    print "get data..."
    conn = psycopg2.connect(host='192.168.199.152', user='cwlgp', password='cwl12345', database='lottery', port='5432')
    df = pd.read_sql(sql, con=conn)

    # 删除name，id 等列
    print "删除name，id 等列..."
    df = df.drop(['name', 'login_date', 'id'], axis=1)

    # 登录时间数值化
    print "登录时间数值化..."
    df = numericalTime(df, 'login_time')

    # 交易时间数值化
    print "交易时间数值化..."
    df = numericalTime(df, 'trade_time')

    # 性别和婚姻数值化
    print "性别和婚姻数值化..."
    df['gender'] = df['gender'].map({'男': 0, '女': 1}).astype(int)
    df['marriage'] = df['marriage'].map({'已婚': 0, '未婚':1}).astype(int)

    # 字符型字段热编码
    print "字符型字段热编码"
    df = OneHotEncode(df, sql_job, 'job')
    df = OneHotEncode(df, sql_address, 'address')
    df = OneHotEncode(df, sql_edu, 'education')
    df = OneHotEncode(df, sql_pay, 'payment')
    df = OneHotEncode(df, sql_risk, 'risk')
    df = OneHotEncode(df, sql_repu, 'reputation')
    df = OneHotEncode(df, sql_gameid, 'game_id')


    # 处理成特征列表
    print "处理成特征列表..."
    featurelist = list()
    for i in range(len(df.index)):
        point = []
        for j in range(len(df.columns)):
            value = df.iloc[i,j]
            if type(value) == list:
               point.extend(value)
            elif type(value) == numpy.ndarray:
                point.extend(value.tolist())
            else:
                point.append(float(value))
        featurelist.append(point)
    features = numpy.array(featurelist)

    # 记录每一列的最大最小值，后面还原时用到
    feature_min = features.min(axis=0)
    feature_max = features.max(axis=0)

    # 特征标准化
    print "特征标准化..."
    features_minmax = minmaxScale(features)

    # kmeans聚类得到中心点和类别
    centers, labels = kmeansCluster(features_minmax, k)

    # 中心点还原
    true_centers = centers * (feature_max-feature_min) + feature_min

    # 中心点保存
    for center in true_centers:
        for i in range(len(center)):
            print center[i]
        SaveToCSV(center.tolist(), k)

    print "df.columns: ", df.columns
    # PCA降纬
    features_new, pca = pcaProcess(features_minmax, 2)

    # 数据降成两纬后重新跑kmeans算法得到的新中心点和类别
    new_centers, new_labels = kmeansCluster(features_new, k)

    # 效果展示
    print "效果展示..."
    showCluster(features_new, k, new_centers, new_labels, totalnum)

    print 'end.'


