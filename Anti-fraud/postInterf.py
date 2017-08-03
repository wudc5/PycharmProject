#coding=utf-8
import os
import json
import commands
import urllib, urllib2

def getRequestInfo(url,accessKey,data,type):
    body_value = {"accessKey": accessKey, "data": data, "type": type}
    body_value1 = urllib.urlencode(body_value)
    # print body_value1
    request = urllib2.Request(url, body_value1)
    # request.add_header(keys, headers[keys])
    result = urllib2.urlopen(request).read()
    return result

if __name__ == "__main__":
    registertime = "1234"
    userid = 7984793
    ip = "110.11.22.33"
    tokenID = "12898"
    phone = "16578349"
    devicedID = "dfsd"
    data_dic = {"tokenId": tokenID, "ip": ip, "deviceId": devicedID, "phone": phone}
    dic = {"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data": data_dic}
    print "dic: ", str(dic)
    interface = 'http://192.168.199.159/v2/saas/login'
    b = "curl -d {0} {1}".format(str(dic), interface)
    print b


    # # curl -d'{"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data":{"tokenId":"136386957","ip":"111.85.43.52","deviceId":"201609230752080df6b1117e456ffb41d4032335b85d133d13742cd1b53662","phone":"13800138000"}}' 'http://192.168.199.159/v2/saas/login'
    # b = "curl -d '{{0}:{1},}' 'http://192.168.199.159/v2/saas/register'"\
    #     .format("accessKey", "WwpIYJ3MiZ0qHCjHiMKz", "data", "registerTime", "accountId", "ip", "phone","tokenId", int(registertime), str(userid), ip, phone, tokenID)
    # print b
    # # a = "curl -d '{\"accessKey\":\"WwpIYJ3MiZ0qHCjHiMKz\",\"data\":{\"tokenId\":\"136386957\",\"text\":\"这是一个测试文本\"},\"type\":\"ECOM\"}' 'http://192.168.199.159/v2/saas/anti_fraud/text'"
    # # p = os.popen(a)
    # # res = p.read()
    # # print res
    # # print type(res)
    # # res = json.loads(res)
    # #
    # # print type(res)
    # print res["detail"]
    # print res["message"]
    # print res["riskLevel"]
    # print res["score"]


# curl -d'{"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data":{"registerTime":1465810229852,"accountId":"136386957","ip":"111.85.43.52","phone":"13347284758","tokenId":"smtest"}}' 'http://192.168.199.159/v2/saas/register'
# curl -d'{"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data":{"tokenId":"136386957","ip":"111.85.43.52","deviceId":"201609230752080df6b1117e456ffb41d4032335b85d133d13742cd1b53662","phone":"13800138000"}}' 'http://192.168.199.159/v2/saas/hongbao'
# curl -d'{"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data":{"tokenId":"136386957","ip":"111.85.43.52","deviceId":"201609230752080df6b1117e456ffb41d4032335b85d133d13742cd1b53662","phone":"13800138000"}}' 'http://192.168.199.159/v2/saas/login'
# curl -d'{"accessKey":"WwpIYJ3MiZ0qHCjHiMKz","data":{"tokenId":"136386957","text":"江泽民"},"type":"ECOM"}' 'http://192.168.199.159/v2/saas/anti_fraud/text'
