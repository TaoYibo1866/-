import urllib.request as urllib
import json

def get(accessToken, mediaId):
    postUrl = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (accessToken, mediaId)
    urlResp = urllib.urlopen(postUrl)
    #jsonDict = json.loads(urlResp.read().decode("UTF-8"))
    contentType = urlResp.info().get('Content-Type')
    if contentType != 'application/json' and contentType != 'text/plain':
        buffer = urlResp.read()   #素材的二进制
        return buffer
        #buffer = urlResp.read()   #素材的二进制
        #fileName = time.asctime() + '.jpg'
        #mediaFile = open('images/' + fileName, "wb")
        #mediaFile.write(buffer)
        #return 'images/' + fileName
