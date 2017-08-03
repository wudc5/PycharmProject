#coding=utf-8
import MySQLdb
import pandas as pd
import numpy
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.metrics import *
from sklearn import svm
from sklearn import tree


def OneHotEncode(df, sql, col):
    onehot_encoder = DictVectorizer()
    kindlist = getDBdata(sql, 'localhost', 'root', '123456', 'lottery')
    kindmaplist = list()
    for kind in kindlist:
        kindmaplist.append({col: kind[0]})
    kindcode = onehot_encoder.fit_transform(kindmaplist).toarray()

    kind_dic = dict()
    for i in range(len(kindlist)):
        kind_dic[kindlist[i][0]] = kindcode[i]
    for i in range(len(df[col])):
        df[col][i] = kind_dic[df[col][i]]
    return df

def getDBdata(sql, host, user, passwd, db):
    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
    cur = conn.cursor()
    cur.execute('SET NAMES UTF8')
    conn.commit()
    oper = cur.execute(sql)
    data = cur.fetchmany(oper)
    cur.close()
    return data


def processMissingValue(df, col):
    df[col] = df[col].map(lambda x: 0 if str(x).replace(' ', '') == '' else x)
    df[col] = df[col].map(lambda x: 0 if x == 'NA' else x)
    df[col] = df[col].map(lambda x: 0 if pd.isnull(x) else x)
    return df

def minmaxScale(features):
    min_max_scaler = preprocessing.MinMaxScaler()
    features_minmax = min_max_scaler.fit_transform(features)
    print "after minmax process: ", features_minmax
    return features_minmax


if __name__ == '__main__':

    print 'start...'
    sql = "select * from antifrauddata where LoE_DI is not null and LoE_DI != 'NA' and (gender = 'f' or gender = 'm') limit 30000"
    sql_course_id = "select course_id from antifrauddata GROUP BY course_id;"
    sql_final_cc_cname_DI = "select final_cc_cname_DI from antifrauddata GROUP by final_cc_cname_DI;"
    sql_LoE_DI = "select LoE_DI from antifrauddata where LoE_DI is not null and LoE_DI != 'NA' GROUP by LoE_DI;"
    conn = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="lottery", charset='utf8')
    df = pd.read_sql(sql, con=conn)


    df =df.drop(['userid_DI', 'registered', 'certified', 'YoB', 'start_time_DI', 'last_event_DI', 'roles', 'incomplete'], axis=1)

    # 处理缺失值
    df = processMissingValue(df, 'viewed')
    df = processMissingValue(df, 'explored')
    df = processMissingValue(df, 'grade')
    df = processMissingValue(df, 'nevents')
    df = processMissingValue(df, 'ndays_act')
    df = processMissingValue(df, 'nplay_video')
    df = processMissingValue(df, 'nchapters')
    df = processMissingValue(df, 'nforum_posts')
    df = processMissingValue(df, 'incomplete_flag')

    print "OneHotEncoding...."
    df = OneHotEncode(df, sql_course_id, 'course_id')
    df = OneHotEncode(df, sql_final_cc_cname_DI, 'final_cc_cname_DI')
    df = OneHotEncode(df, sql_LoE_DI, 'LoE_DI')

    # gender transform...
    df['gender'] = df['gender'].map({'m': 1, 'f': 0}).astype(int)
    print "df['incomplete_flag']: ", df['incomplete_flag']

    labels = df['incomplete_flag']
    df = df.drop(['incomplete_flag'], axis=1)

    # 处理成特征列表
    print "处理成特征列表..."
    featurelist = list()
    for i in range(len(df.index)):
        point = []
        for j in range(len(df.columns)):
            value = df.iloc[i, j]
            print "i: {0}, j:{1}".format(i, j)
            print "value: ", value
            if type(value) == list:
                point.extend(value)
            elif type(value) == numpy.ndarray:
                point.extend(value.tolist())
            else:
                point.append(float(value))
        featurelist.append(point)

    print "columns: ", df.columns
    labels = labels.tolist()
    labels = [int(label) for label in labels]

    print "data_size: ", len(featurelist)

    train_size = int(0.8 * len(featurelist))
    print "train_size: ", train_size
    X_train = featurelist[:train_size]
    Y_train = labels[:train_size]

    X_test = featurelist[train_size:]
    Y_test = labels[train_size:]

    # 逻辑回归模型预测
    clf_LR = LogisticRegression(C=0.001, penalty='l2')
    clf_LR.fit_transform(X_train, Y_train)
    predictions_LR = clf_LR.predict(X_test)
    print(classification_report(Y_test, predictions_LR))
    print('Precision_LR: ', precision_score(Y_test, predictions_LR))
    print('Recall_LR: ', recall_score(Y_test, predictions_LR))
    print('Accuracy_LR: ', accuracy_score(Y_test, predictions_LR))

    # svm模型预测
    clf_svm = svm.SVC()
    clf_svm.fit(X_train, Y_train)
    predictions_dt = clf_svm.predict(X_test)
    print(classification_report(Y_test, predictions_dt))
    print('Precision_svm: ', precision_score(Y_test, predictions_dt))
    print('Recall_svm: ', recall_score(Y_test, predictions_dt))
    print('Accuracy_svm: ', accuracy_score(Y_test, predictions_dt))

    # 决策树模型预测
    clf_dt = tree.DecisionTreeClassifier()
    clf_dt = clf_dt.fit(X_train, Y_train)
    predictions_dt = clf_dt.predict(X_test)
    print "predictions_dt: ", predictions_dt
    print "Y_test: ", Y_test
    print(classification_report(Y_test, predictions_dt))
    print('Precision_dt: ', precision_score(Y_test, predictions_dt))
    print('Recall_dt: ', recall_score(Y_test, predictions_dt))
    print('Accuracy_dt: ', accuracy_score(Y_test, predictions_dt))






