# -*- coding: utf-8 -*-
from django.contrib import admin
from wx.models import Administrator, Customer, ImageReport
from django.utils.html import format_html

class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('address', 'group')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('address', 'openid')

class ImageReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'address', 'qrcode', 'send', 'file_link')
    def file_link(self, obj):
        if obj.image:
            return format_html("<a href='%s' download>Download</a>" % (obj.image.url,))
        else:
            return '无'
    file_link.short_description = '下载'

admin.site.register(Administrator, AdministratorAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ImageReport, ImageReportAdmin)