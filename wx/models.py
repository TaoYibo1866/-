# -*- coding: utf-8 -*-
from django.db import models
import django.utils.timezone as timezone

class Administrator(models.Model):
    class Meta:
        verbose_name = '管理员'
        verbose_name_plural = '管理员'
    openid = models.CharField(max_length=100, default=None)
    address = models.EmailField('邮箱', default=None)
    group = models.IntegerField('所在组', default=0)

    def __str__(self):
        return str(self.address)

class Customer(models.Model):
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    openid = models.CharField(max_length=100, default=None)
    address = models.CharField('联系方式', max_length=100, default=None)

    def __str__(self):
        return str(self.address)

class ImageReport(models.Model):
    class Meta:
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
    address = models.CharField(max_length=100, default=None)
    date = models.DateTimeField('日期', default=timezone.now)
    qrcode = models.TextField('二维码', default=None)
    image = models.ImageField('图片', upload_to='images/', default=None)
    send = models.BooleanField('邮件发送成功', default=False)

    def __str__(self):
        return str(self.date)