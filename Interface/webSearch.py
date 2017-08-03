# -*- coding: utf-8 -*-

import sys
import urllib
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    headers = {
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
               'Authorization': 'TEAqbDnNktT6',
               'token': 'TEAqbDnNktT6'
               }
    id = '22822'
    startUrl = 'https://open.api.tianyancha.com/services/v3/newopen/baseinfo.json?id=%s' % urllib.quote(id)
    resultPage = requests.get(startUrl, headers=headers)  # 在请求中设定头
    print resultPage.text

if __name__ == '__main__':
    main()