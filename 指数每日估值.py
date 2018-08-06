import re
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import pandas as pd
import os
import datetime


url_dj = 'https://danjuanapp.com/djapi/index_eva/dj'
url_qm = 'https://qieman.com/idx-eval'
path = 'D://每日估值/'


# 获取估值的网站页面
def get_page(url):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option)
    driver.get(url)
    text = driver.page_source
    driver.quit()
    return text

# 解析蛋卷基金页面


def parse_dj(text):
    pattern = re.compile(
        '{"id":\d+,"index_code":"(.*?)","name":"(.*?)","pe":(.*?),"pb":(.*?),"pe_percentile":(.*?),"pb_percentile":(.*?),"roe":(.*?),"yeild":(.*?),"ts.*?eva_type":"(.*?)".*?}', re.S)
    results = re.findall(pattern, text)
    list_dj = []
    for result in results:
        eval_dict = {}
        eval_dict['index_code'] = result[0]
        eval_dict['name'] = result[1]
        eval_dict['pe'] = result[2]
        eval_dict['pb'] = result[3]
        eval_dict['pe_percentile'] = str(
            round(float(result[4]) * 100, 2)) + '%'
        eval_dict['pb_percentile'] = str(
            round(float(result[5]) * 100, 2)) + '%'
        eval_dict['roe'] = str(round(float(result[6]) * 100, 2)) + '%'
        eval_dict['yeild'] = str(round(float(result[7]) * 100, 2)) + '%'
        eval_dict['type'] = result[8]
        list_dj.append(eval_dict)

    return list_dj

# 解析且慢页面


def parse_qm(text):

    html = BeautifulSoup(text, 'lxml')
    list1 = html.find('div', class_='flex-table__67b31')
    # list2 为 各个指数的估值分块
    list2 = list1.contents
    list_qieman = []
    count = 0
    # 且慢估值的排名
    rank = 1
    for each in list2[1:]:
        for result in each.contents:
            p = result.find_all('p')
            if not p:
                continue
            dict_qieman = {}
            dict_qieman['name'] = p[0].span.text
            if dict_qieman['name'] == '可选消费':
                dict_qieman['name'] = '全指可选'
            elif dict_qieman['name'] == '创业板指':
                dict_qieman['name'] = '创业板'
            elif dict_qieman['name'] == '恒生国企':
                dict_qieman['name'] = '国企指数'
            elif dict_qieman['name'] == '纳斯达克100':
                dict_qieman['name'] = '纳指100'
            elif dict_qieman['name'] == '500低波动':
                dict_qieman['name'] = '500低波'
            dict_qieman['pe/pb'] = p[1].span.text
            if p[2].span.text != '--':
                dict_qieman['percent_qm'] = p[2].span.text + '%'
            dict_qieman['max'] = p[3].span.text
            dict_qieman['min'] = p[4].span.text
            dict_qieman['roe_qm'] = p[5].span.text + '%'
            if count == 0:
                dict_qieman['type_qm'] = 'low'
            elif count == 1:
                dict_qieman['type_qm'] = 'mid'
            elif count == 2:
                dict_qieman['type_qm'] = 'high'
            elif count == 3:
                dict_qieman['type_qm'] = 'unsort'
            dict_qieman['rank_qm'] = rank
            rank += 1

            list_qieman.append(dict_qieman)
        count += 1
    return list_qieman


def join_dict(list_main, list_sec):
    name_list = []
    for each in list_main:
        #     print(name)
        name_list.append(each['name'])

    for i in list_sec:
        if i['name'] not in name_list:
            list_main.append(i)
        else:
            for j in list_main:
                if j['name'] == i['name']:
                    list_main[list_main.index(j)].update(i)

    return list_main


def save_tocsv(data, path):
    columns = ['index_code', 'name', 'pe',
               'pe_percentile', 'pb', 'pb_percentile', 'yeild', 'roe', 'pe/pb', 'percent_qm', 'max', 'min', 'rank_qm', 'roe_qm',
               'type', 'type_qm']
    df = pd.DataFrame(data)
    path = path.rstrip('\\')
    # 判断目录是否存在，若不存在，则创建
    if not os.path.exists(path):
        os.makedirs(path)
    # 获取现在的时间戳
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    df.to_csv(path + '\\' + now + '.csv',
              encoding='utf_8_sig', columns=columns)
    print('保存成功')


text_qm = get_page(url_qm)
text_dj = get_page(url_dj)
list_qieman = parse_qm(text_qm)
list_dj = parse_dj(text_dj)
list_join = join_dict(list_dj, list_qieman)
save_tocsv(list_join, path)
