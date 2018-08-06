import requests
import re
import json

#抓取百度文库的文章，只支持pdf 和 word



#模拟手机登录比较好抓
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36'
}


def start_request(url):
    '''
    得到原始文档的text
    url : 输入文档的链接
    返回 文档的text，标题和文档类型


    '''

    response = requests.get(url, headers=headers).text
    title = re.search('<title>(.*?)</title>', response, re.S).group(1)
    doctype = re.search('"docTypeName":"(.*?)"', response, re.S).group(1)
    print(doctype)
    return response, title, doctype


def get_page(url, params):
    '''
    url : ajax 分页链接
    params ： ajax的后缀参数
    '''
    resp = requests.get(url, headers=headers, params=params).text
    resp = resp.encode(
        'utf-8').decode('unicode_escape')  # unciode转为utf-8 然后转为中文
    response = re.sub(r',"no_blank":true', '', resp)
    result = re.findall('c":"(.*?)"}', response)  # 找到c下面的所有文字
    result = '\n'.join(result)  # 将文字放在一起，分段
    # print(result)
    return(result)


def get_params_word(text):
    '''
    从原始链接的text中获取所需参数
    params: dict
    params_2 :list
    '''
    # title = re.search('<title>(.*?)</title>', text, re.S).group(1)
    # print(title)
    pattern = re.compile(
        '"&md5sum=(.*?)&sign=(.*?)&rtcs_flag=(.*?)&rtcs_ver=(.*?)".*?rsign":"(.*?)"', re.S)
    # 找到最初直接得到的几个参数
    params_1 = pattern.search(text)
    params = {
        'md5sum': params_1.group(1),
        'sign': params_1.group(2),
        'rtcs_flag': params_1.group(3),
        'rtcs_ver': params_1.group(4),
        "width": 176,
        "type": "org",
        'rsign': params_1.group(5)

    }
# 找到分页参数
    pattern_2 = re.compile('"merge":"(.*?)".*?page":(.*?)}', re.S)
    params_2 = pattern_2.findall(text)
    return params, params_2


def get_params_pdf(text):
    '''
    从原始链接的text中获取所需参数
    params: dict
    params_2 :list
    '''
    # title = re.search('<title>(.*?)</title>', text, re.S).group(1)
    # print(title)
    pattern = re.compile(
        '"&md5sum=(.*?)&sign=(.*?)".*?rsign":"(.*?)"', re.S)
    # 找到最初直接得到的几个参数
    params_1 = pattern.search(text)
    params = {
        'md5sum': params_1.group(1),
        'sign': params_1.group(2),
        "width": 176,
        "type": "org",
        'rsign': params_1.group(3)

    }
# 找到分页参数
    pattern_2 = re.compile('"merge":"(.*?)".*?page":(.*?)}', re.S)
    params_2 = pattern_2.findall(text)
    return params, params_2


def save_to_text(i, title, result):
    with open(title + '.txt', 'a+') as f:
        f.write(result + '\n\n')
        f.write('第 %s 页 \n\n' % i)


def main(start_url):
    text, title, doctype = start_request(start_url)
    if doctype == 'word':
        params, params_2 = get_params_word(text)
    elif doctype == 'pdf':
        params, params_2 = get_params_pdf(text)
    else:
        return None
    doc_url = "https://wkretype.bdimg.com/retype/merge/" + start_url[29:-5]
    for i in range(len(params_2)):
        # print('第 %s 页' % (i + 1))
        doc_page = '_'.join([k for k, v in params_2[i:i + 1]])
        params['pn'] = i + 1
        params['rn'] = 1
        params['callback'] = 'sf_edu_wenku_retype_doc_jsonp_' + \
            str(params['pn']) + "_1"
        params['range'] = doc_page
        result = get_page(doc_url, params)
        save_to_text(i + 1, title, result)
    print('保存成功')


if __name__ == '__main__':
    url = "https://wenku.baidu.com/view/aa31a84bcf84b9d528ea7a2c.html"
    # url = 'https://wenku.baidu.com/view/ab1863f14a7302768f9939e9.html'
    url = 'https://wk.baidu.com/view/6e6d1250e87101f69e319585'

    main(url)
