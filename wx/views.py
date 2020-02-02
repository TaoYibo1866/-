import hashlib
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import reply, media, basic, customize

@csrf_exempt
def handle(request):
    #只在绑定服务器时起效
    if request.method == 'GET':
        try:
            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            echostr = request.GET.get('echostr')
            token = 'gdhb'
            hashlist = [token, timestamp, nonce]
            hashlist.sort()
            hashstr = ''.join([i for i in hashlist])
            sha1 = hashlib.sha1()
            sha1.update(hashstr.encode('utf-8'))
            hashcode = sha1.hexdigest()
            if hashcode == signature:
                return HttpResponse(echostr)
            return HttpResponse('success')
        except Exception as argument:
            return HttpResponse(argument)
    #实际的业务逻辑
    elif request.method == 'POST':
        try:
            data = request.body
            xml_data = ET.fromstring(data)
            msg_type = xml_data.find('MsgType').text
            server = xml_data.find('ToUserName').text
            openid = xml_data.find('FromUserName').text
            if msg_type == 'text':
                content = xml_data.find('Content').text
                reply_msg = customize.textHandler(content, xml_data)
            elif msg_type == 'image':
                media_id = xml_data.find('MediaId').text
                access_token = basic.Basic().get_access_token()
                buffer = media.get(access_token, media_id)
                reply_msg = customize.imgHandler(buffer, xml_data)
            else:
                reply_msg = reply.TextMsg(openid, server, '暂不支持此类型消息')
            return HttpResponse(reply_msg.send())
        except Exception as argument:
            reply_msg = reply.TextMsg(openid, server, argument)
            return HttpResponse(reply_msg.send())
