#coding=utf-8

import urllib, urllib2

url = 'https://open.api.tianyancha.com/services/v3/newopen/searchV2.json?word={0}'.format(urllib.urlencode('北京百度网讯科技有限公司'))
headers = {
    # 'Host':'www.super-ping.com',
    #         'Connection':'keep-alive',
    #         'Cache-Control':'max-age=0',
    #         'Accept': 'text/html, */*; q=0.01',
    #                 'X-Requested-With': 'XMLHttpRequest',
    #                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
    #                 'DNT':'1',
    #                 'Referer': 'http://www.super-ping.com/?ping=www.google.com&locale=sc',
    #                 'Accept-Encoding': 'gzip, deflate, sdch',
    #                 'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6',
            'Authorization': 'TEAqbDnNktT6',
            'token': '阿尔法金服'
                    }
data = None
req = urllib2.Request(url, data, headers)
response = urllib2.urlopen(req)
compressedData = response.read()
print compressedData