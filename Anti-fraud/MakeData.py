#coding=utf-8
import random
import psycopg2, re

def getdataFromPG(sql, host, user, passwd, db):          # 得到PG中数据
    conn = psycopg2.connect(host=host, user=user, password=passwd, database=db, port='5432')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def saveToFile(row, filepath):
    with open(filepath, 'a') as wp:
        wp.write(row)
        wp.close()

def makeRegisterInfo():
    with open("E:\lingzhong\manmadedata/antifraued/antifraued.txt") as rp:
        lines = rp.readlines()
        for line in lines:
            registertime = str(random.randint(827475754, 1458627754))
            year = str(random.randint(2000, 2016))
            month = random.randint(1, 12)
            if month < 10:
                month = "0"+str(month)
            else:
                month = str(month)
            day = random.randint(1, 30)
            if day< 10:
                day = "0"+str(day)
            else:
                day = str(day)
            hour = random.randint(0, 23)
            if hour < 10:
                hour = "0" + str(hour)
            else:
                hour = str(hour)
            mins = random.randint(0, 59)
            if mins<10:
                mins = "0" + str(mins)
            else:
                mins = str(mins)
            seconds = random.randint(0,59)
            if seconds< 10:
                seconds = "0" + str(seconds)
            else:
                seconds = str(seconds)
            strnums = '0123456789abcdefghijklmnopqrstuvwxyz'
            suffix = ""
            for i in range(0, 48):
                suffix = suffix + strnums[random.randint(0, len(strnums)-1)]
            deviceID = year + month + day + hour + mins + seconds + suffix
            print "deviceID: ", deviceID

            # deviceID = str(random.randint(2000, 2016)) + ('0'+str(random.randint(1,12))) if random.randint(1,12)<10 else (str(random.randint(1,12)))
            row = registertime + "|" + deviceID + "|" + line
            print "row: ", row
            saveToFile(row, "E:\lingzhong\manmadedata/antifraued/RegisterInfo.txt")

def makeLoginInfo():
    sql_ip = 'select ip from "tradeData"'
    sql_tokenID = 'select "tokenID" from "tradeData"'
    iplist = getdataFromPG(sql_ip, "192.168.199.152", "gpadmin", "1qaz@WSX", "lottery")
    tokenIDlist = getdataFromPG(sql_tokenID, "192.168.199.152", "gpadmin", "1qaz@WSX", "lottery")
    for i in range(0, 1000000):
        ip = iplist[random.randint(0, len(iplist)-1)][0]
        tokenID = tokenIDlist[random.randint(0, len(tokenIDlist)-1)][0]
        userid = str(random.randint(1, 1000000))
        row = "{0}|{1}|{2}|{3}".format(i, userid, ip, tokenID)
        saveToFile(row+"\n", "E:\lingzhong\manmadedata/antifraued/LoginInfo.txt")

def makeTextContent():
    with open("E:\lingzhong\manmadedata/antifraued/text2.txt") as rp:
        lines = rp.readlines()
        while True:
            num = random.randint(0, len(lines)-1)
            content = re.split("，|、|：| |,", lines[num])
            # content = lines[num].split("：、，？")
            words = content[random.randint(0, len(content)-1)].replace(" ", "")
            if len(words) > 1:
                break
        print "***********words:  ", words
        print "***********length of words:  ", len(words)
        return words

def makeTestInfo():
    sql_data = 'select "id", "tokenID" from "AntiFraued_RegisterInfo"'
    datalist = getdataFromPG(sql_data, "192.168.199.152", "gpadmin", "1qaz@WSX", "lottery")
    for i in range(0, len(datalist)-1):
        data = datalist[i]
        userid = data[0]
        tokenid = data[1]
        text = makeTextContent()
        print data[0], data[1], text
        row = "{0}|{1}|{2}|{3}\n".format(i, userid, tokenid, text)
        saveToFile(row, "E:\lingzhong\manmadedata/antifraued/TextInfo.txt")



if __name__ == "__main__":
    # makeRegisterInfo()
    # makeRegisterInfo()
    # makeLoginInfo()
    makeTestInfo()