# coding=utf-8
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans
import psycopg2
import MySQLdb
import pandas as pd
import numpy
from sklearn import preprocessing
from scipy.spatial.distance import cdist
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn import metrics

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def OneHotEncode(df, sql, col):
    onehot_encoder = DictVectorizer()
    kindlist = GetDataFromPG(sql, '192.168.199.152', 'cwlgp', 'cwl12345', 'lottery')
    # kindlist = getDataFromDB(sql, 'localhost', 'root', '123456', 'lottery')

    kindmaplist = list()
    for kind in kindlist:
        kindmaplist.append({col: kind[0]})
    print "maplist: ", kindmaplist
    kindcode = onehot_encoder.fit_transform(kindmaplist).toarray()
    print "kindcode: ", kindcode

    kind_dic = dict()
    for i in range(len(kindlist)):
        kind_dic[kindlist[i][0]] = kindcode[i]
        print kindcode[i]
    for i in range(len(df[col])):
        df[col][i] = kind_dic[df[col][i]]
        print df[col][i]
    print "kind_dic: ", kind_dic
    return df


def GetDataFromPG(sql, host, user, passwd, db):
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def getDataFromDB(sql, host, user, passwd, db):
    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def numericalTime(df, col):
    for i in range(len(df[col])):
        hour = int(df[col][i][:2])
        if hour >= 0 and hour < 8:
            df[col][i] = [1, 0, 0]
        elif hour >= 8 and hour < 16:
            df[col][i] = [0, 1, 0]
        else:
            df[col][i] = [0, 0, 1]
    return df

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

def compareSC(X):      #查看轮廓系数, 注意X中为二维特征数据
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b']
    markers = ['o', 's', 'D', 'v', '^', 'p', '*', '+']
    tests = [2, 3, 4, 5]
    subplot_counter = 1
    for t in tests:
        subplot_counter += 1
        plt.subplot(3, 2, subplot_counter)
        kmeans_model = KMeans(n_clusters=t).fit(X)
        for i, l in enumerate(kmeans_model.labels_):
            plt.plot(X[i][0], X[i][1], color=colors[l], marker=markers[l], ls='None')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.title('K = %s, Contour coefficient = %.03f' % (t, metrics.silhouette_score(X, kmeans_model.labels_, metric='euclidean')))
    plt.show()

def getSuitableK(X, totalnum):
    K = range(1, 10)
    meandistortions = []
    for k in K:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(X)
        meandistortions.append(sum(numpy.min(cdist(X, kmeans.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0])
    plt.plot(K, meandistortions, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Average distortion')
    plt.title('Select the appropriate K value')
    plt.savefig('{0}_jibian.png'.format(totalnum))
    plt.show()



if __name__ == '__main__':
    print 'start..'
    totalnum = sys.argv[1]
    print "totalnum: ", totalnum
    sql = "select * from personas order by id limit {0}".format(totalnum)
    sql_job = "select job from personas group by job"
    sql_address = "select address from personas group by address"
    sql_edu = "select education from personas group by education"
    sql_pay = "select payment from personas group by payment"
    sql_risk = "select risk from personas group by risk"
    sql_repu = "select reputation from personas group by reputation"
    sql_gameid = "select game_id from personas group by game_id"

    # get data
    print "get data..."
    conn = psycopg2.connect(host='192.168.199.152', user='cwlgp', password='cwl12345', database='lottery', port='5432')
    # conn = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="lottery")
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
    df['marriage'] = df['marriage'].map({'已婚': 0, '未婚': 1}).astype(int)

    # 字符型字段热编码
    print "字符型字段热编码..."
    onehot_encoder = DictVectorizer()
    df = OneHotEncode(df, sql_job, 'job')
    df = OneHotEncode(df, sql_address, 'address')
    df = OneHotEncode(df, sql_edu, 'education')
    df = OneHotEncode(df, sql_pay, 'payment')
    df = OneHotEncode(df, sql_risk, 'risk')
    df = OneHotEncode(df, sql_repu, 'reputation')
    df = OneHotEncode(df, sql_gameid, 'game_id')

    # 处理成特征列表
    print "处理特征列表..."
    featurelist = list()
    for i in range(len(df.index)):
        point = []
        for j in range(len(df.columns)):
            value = df.iloc[i, j]
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

    # 计算畸变程度选取合适的K
    print "计算畸变程度选取合适的K..."
    getSuitableK(features_minmax, totalnum)

    # pca 降纬
    print "pca 降纬..."
    features_new, pca = pcaProcess(features_minmax, 2)

    # 比较轮廓系数
    print "比较轮廓系数..."
    compareSC(features_new)