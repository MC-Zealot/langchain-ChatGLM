#!/usr/bin/python
# -*- coding: UTF-8 -*-
import textfsm
import os

# os.chdir('/mnt/d/project/Netmiko_learn/textFSM_learn')

traceroute = '''
第二节公司简介和主要财务指标
一、公司信息 
['股票简称', '华灿光电', '股票代码', '300323']
['公司的中文名称', '华灿光电股份有限公司', '', '']
['公司的中文简称', '华灿光电', '', '']
['公司的外文名称（如有）', 'HC SemiTek Corporation', '', '']
['公司的外文名称缩写（如有）', 'HC SemiTek', '', '']
['公司的法定代表人', '郭瑾', '', '']
['注册地址', '武汉市东湖开发区滨湖路8号', '', '']
['注册地址的邮政编码', '430223', '', '']
['', '2009年10月19日由武汉市东湖新技术开发区大学园路武大科技园创业楼2015室变更为现注册地址', '', '']
['公司注册地址历史变更情况', '', '', '']
['办公地址', '武汉市东湖开发区滨湖路8号', '', '']
['办公地址的邮政编码', '430223', '', '']
['公司国际互联网网址', 'www.HCSemiTek.com', '', '']
['电子信箱', 'zq@hcsemitek.com', '', '']
二、联系人和联系方式 
['', '董事会秘书', '证券事务代表'] 
['姓名', '胡正然（代行人）', '张晓雪'] 
['联系地址', '武汉市东湖开发区滨湖路8号', '武汉市东湖开发区滨湖路8号']
['电话', '027-81929003', '027-81929003']
['传真', '027-81929003', '027-81929003']
['电子信箱', 'zq@hcsemitek.com', 'zq@hcsemitek.com']
三、信息披露及备置地点 
['公司披露年度报告的证券交易所网站', 'www.cninfo.com.cn']
['公司披露年度报告的媒体名称及网址', '《上海证券报》、《中国证券报》、《证券时报》、《证券日报》']
['公司年度报告备置地点', '证券事务部']
'''

with open('templates/info.template') as template:
    fsm = textfsm.TextFSM(template)
    result = fsm.ParseText(traceroute)

print(fsm.header)
# print(result)
comp_info={}
for res in result:
    comp_info[res[0]] = res[1]
    print(res[0] +"是：\t" +res[1])

# print(comp_info)