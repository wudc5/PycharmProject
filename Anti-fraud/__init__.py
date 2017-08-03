#coding=utf-8
import numpy as np
import pandas as pd
import MySQLdb

sql = "select * from antifrauddata  limit 100000"
# datalist = antifraud.getDBdata(sql, 'localhost', 'root', '123456', 'lottery')

conn = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="lottery", charset='utf8')
df = pd.read_sql(sql, con=conn)
# print df

# print df['final_cc_cname_DI']
# # df['roles'] = df['roles'].map(lambda x: 0 if pd.isnull(x) else x)
# df['final_cc_cname_DI'] = df['final_cc_cname_DI'].map(lambda x: 0 if x == 'Germany'  else x)
# # df['gender'] = df['gender'].map({'NA': 0, 'o': 1, 'f': 2, 'm': 3})
# # print df['roles']
# print df['final_cc_cname_DI']
# print type(df['final_cc_cname_DI'])

print df['LoE_DI']
# df['LoE_DI'] = df['LoE_DI'].map({"NA": 100, None: 1})
# df['LoE_DI'] = df['LoE_DI'].map(lambda x: 0 if pd.isnull(x) else x)
df['LoE_DI'] = df['LoE_DI'].map(lambda x: 0 if x == None else x)
df['LoE_DI'] = df['LoE_DI'].map(lambda x: 0 if x == "NA" else x)
print df['LoE_DI']