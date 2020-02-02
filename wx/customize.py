# -*- coding: utf-8 -*-
import re
import difflib
import io
import time
from PIL import Image
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files.base import ContentFile
from pyzbar.pyzbar import decode, ZBarSymbol

from wx.models import Administrator, Customer, ImageReport
from . import reply


def inv(code):
    #解出验证码
    code = int(code)
    ans = [0, 0, 0, 0]
    ans[0] = code//1000
    ans[1] = code % 1000//100
    ans[2] = code % 1000 % 100//10
    ans[3] = code % 1000 % 100 % 10
    for i in range(4):
        if ans[i] % 2 == 0:
            ans[i] = str(ans[i] + 1)
        else:
            ans[i] = str(ans[i] - 1)
    temp = ans[0]
    ans[0] = ans[2]
    ans[2] = temp
    ans = ''.join(ans)
    return ans

def send(address, body, img_name=None, img_data=None):
    #发送邮件
    email = EmailMessage(
        subject='工大航博故障反馈系统',
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=address
    )
    if img_name is not None and img_data is not None:
        email.attach(img_name, img_data)
    try:
        ret = email.send(fail_silently=False)
        return ret
    except Exception as argument:
        print(argument)
        return False

def findSim(content, command_list):
    #找出最接近的字符串
    ratio = 0.0
    for i in command_list:
        _ratio = difflib.SequenceMatcher(None, content, i).quick_ratio()
        if _ratio > ratio:
            ratio = _ratio
            sim = i
    if ratio > 0.1:
        return '您想输入的是否为: %s' % sim
    return "\'%s\'不是可执行命令" % content

def imgHandler(buffer, xml_data):
    img = Image.open(io.BytesIO(buffer))
    server = xml_data.find('ToUserName').text
    openid = xml_data.find('FromUserName').text
    time_stamp = xml_data.find('CreateTime').text
    try:
        cust = Customer.objects.get(openid=openid)
    except Customer.DoesNotExist:
        is_cust = False
    else:
        is_cust = True
    if not is_cust:
        text = '您尚未注册为用户'
        reply_msg = reply.TextMsg(openid, server, text)
        return reply_msg
    try:
        gry = img.convert('L')
        width, height = img.size
        binary = gry.point(lambda x: 0 if x < 128 else 255, '1')
    except:
        text = '图片错误'
        reply_msg = reply.TextMsg(openid, server, text)
        return reply_msg
    try:
        res = decode(binary, symbols=[ZBarSymbol.QRCODE])[0]
        point1 = res.polygon[0]
        point2 = res.polygon[1]
        area = (point1.x - point2.x)**2 + (point1.y - point2.y)**2
        qrcode = res.data.decode('utf-8').encode('shift-jis').decode('utf-8')
        data = qrcode.split('/')
        assert len(data[0]) == 4
        code = data[0]
        ratio = int(data[1])
        group = int(data[2])
        content = '/'.join(data[3:])
        assert content != ''
    except:
        text = '二维码错误'
        reply_msg = reply.TextMsg(openid, server, text)
        return reply_msg
    if ratio * width * height < area * 100:
        text = '覆盖过少，请重新拍照'
        reply_msg = reply.TextMsg(openid, server, text)
        return reply_msg
    ans = inv(code)
    text = '验证码: %s' % ans
    reply_msg = reply.TextMsg(openid, server, text)
    try:
        time_array = time.localtime(int(time_stamp))
        date = time.strftime("%Y--%m--%d %H:%M:%S", time_array)
        name = '%s.%s' % (date, img.format)
        report = ImageReport(address=cust.address, qrcode=qrcode)
        report.image.save(name, ContentFile(buffer))
        report.save()
        admin = Administrator.objects.filter(group=group)
        if admin:
            to_who = [settings.EMAIL_HOST_USER]
            for i in admin:
                to_who.append(i.address)
            content = '用户联系方式:' + report.address + '\n' + '错误信息:' + content
            if send(to_who, content, report.image.name, report.image.read()):
                report.send = True
        report.save()
        return reply_msg
    except Exception as argument:
        print(argument)
        return reply_msg

def textHandler(content, xml_data):
    command_list = ['管理员注册xxxxxxx@qq.com', '加入组x', '显示所有管理员',
                    '显示所有用户', '管理员注销', '用户注册xxxxx', '用户注销', '使用指南']
    server = xml_data.find('ToUserName').text
    openid = xml_data.find('FromUserName').text
    regis_pattern = r'^管理员注册[1-9][0-9]{4,}@qq.com$'
    group_pattern = r'^加入组\d$'
    decode_pattern = r'^解码[0-9]{4}$'

    #分辨是用户还是管理员
    try:
        admin = Administrator.objects.get(openid=openid)
    except Administrator.DoesNotExist:
        is_admin = False
    else:
        is_admin = True
    try:
        cust = Customer.objects.get(openid=openid)
    except Customer.DoesNotExist:
        is_cust = False
    else:
        is_cust = True
    #管理员命令部分
    if re.match(regis_pattern, content) is not None:
        address = content[5:]
        if send([address], '测试邮件'):
            if is_admin:
                admin.address = address
                admin.save()
                text = '新的绑定邮箱为%s' % admin.address
            else:
                admin = Administrator(openid=openid, address=address)
                admin.save()
                text = '您已成为管理员'
        else:
            text = '测试邮件发送失败，请检查您的邮箱是否正确'
        reply_msg = reply.TextMsg(openid, server, text)
    elif re.match(group_pattern, content) is not None:
        if is_admin:
            admin.group = int(content[-1])
            admin.save()
            text = '%s已加入组%d' % (admin.address, admin.group)
        else:
            text = '您没有管理员权限'
        reply_msg = reply.TextMsg(openid, server, text)
    elif content == '显示所有管理员':
        if is_admin:
            text = '组员如下\n'
            i = 1
            for admin in Administrator.objects.all():
                text = text + '%d: %s 组%d' % (i, admin.address, admin.group)
                i = i+1
        else:
            text = '您没有管理员权限'
        reply_msg = reply.TextMsg(openid, server, text)
    elif content == '显示所有用户':
        if is_admin:
            if Customer.objets.all().first is None:
                text = '暂时没有用户注册'
            else:
                text = '用户如下\n'
                i = 1
                for cust in Customer.objects.all():
                    text = text + '%d: %s' % (i, cust.address)
                    i = i+1
        else:
            text = '您没有管理员权限'
        reply_msg = reply.TextMsg(openid, server, text)
    elif content == '管理员注销':
        if is_admin:
            admin.delete()
            text = '您已不是管理员'
        else:
            text = '您没有管理员权限'
        reply_msg = reply.TextMsg(openid, server, text)
    #非管理员部分
    elif content[0:4] == '用户注册':
        address = content[4:]
        if is_cust:
            cust.address = address
            cust.save()
            text = '新的联系方式为%s' % cust.address
        else:
            cust = Customer(openid=openid, address=address)
            cust.save()
            text = '注册成功'
        reply_msg = reply.TextMsg(openid, server, text)
    elif content == '用户注销':
        if is_cust:
            cust.delete()
            text = '您已不是用户'
        else:
            text = '您尚未注册为用户'
        reply_msg = reply.TextMsg(openid, server, text)
    elif re.match(decode_pattern, content) is not None:
        code = content[2:]
        text = '验证码: ' + inv(code)
        reply_msg = reply.TextMsg(openid, server, text)
    elif content == '使用指南':
        text = '待添加'
        reply_msg = reply.TextMsg(openid, server, text)
    else:
        text = findSim(content, command_list)
        reply_msg = reply.TextMsg(openid, server, text)
    return reply_msg