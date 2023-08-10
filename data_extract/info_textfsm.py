#!/usr/bin/python
# -*- coding: UTF-8 -*-
import textfsm
import os

# os.chdir('/mnt/d/project/Netmiko_learn/textFSM_learn')

traceroute = '''
第二节公司简介和主要财务指标
一、公司信息
['股票简称', '华灿光电', '股票代码', '300323']
['公司的中文名称', '华灿光电股份有限公司', 'a', '2']
['公司的中文简称', '华灿光电', '', '']
['公司的外文名称（如有）', 'HC SemiTek Corporation', '2', '3']
['公司的外文名称缩写（如有）', 'HC SemiTek', 'a', 'a']
['公司的法定代表人', 'SemiTek', 'a', '3']
['注册地址', '武汉市东湖开发区滨湖路8号', '', '']
['注册地址的邮政编码', '430223', '', '']
['', '2009年10月19日由武汉市东湖新技术开发区大学园路武大科技园创业楼2015室变更为现注册地址', '', '']
['公司注册地址历史变更情况', '', '', '']
['办公地址', '武汉市东湖开发区滨湖路8号', '', '']
['办公地址的邮政编码', '430223', '', '']
['公司国际互联网网址', 'www.HCSemiTek.com', '', '']
['电子信箱', 'zq@hcsemitek.com', '', '']
'''

with open('templates/info.template') as template:
    fsm = textfsm.TextFSM(template)
    result = fsm.ParseText(traceroute)

print(fsm.header)
# print(result)
comp_info={}
for res in result:
    comp_info[res[0]] = res[1]
    # print(res)

print(comp_info)