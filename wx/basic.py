import urllib.request as urllib
import time
import json

class Basic:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0
    def __real_get_access_token(self):
        appId = "wxffdfae997d5a1371"
        appSecret = "b1099b22dc88e4b019e830e5b6f4b5f9"
        postUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appId, appSecret)
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read().decode("UTF-8"))
        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']
    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken
    def run(self):
        while(True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()
