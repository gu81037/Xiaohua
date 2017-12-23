#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#导入基础库
import re
import os
import requests
from bs4 import BeautifulSoup
from hashlib import md5
from multiprocessing import Pool


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}


def get_page_index(url):    #获得初始网页的html
        print(url)

        try:
            response = requests.get(url, headers = headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            html = response.text
            pattern = re.compile('<a target="_blank" href="(.*?)">', re.S)  #正则匹配html中含有的所有的图片组
            result = re.findall(pattern, html)
            result = result[:-1][::2]   #观察结果发现末尾多了一个地址， 并且所有地址都重复了，所以将重复的地址剔除了
            return result
        except:
            return None


def parse_page_index(result):

    for url in result:  #对得到的结果每一个图片地址进行处理
        r = requests.get(url, headers = headers)
        r.encoding = r.apparent_encoding
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').get_text().replace('1/','') #找到页面中title信息
        pages_pattern = re.compile('共(\w{1,3})页:')  #得到这组图片共有多少张
        pages = int(re.findall(pages_pattern, html)[0]) #将结果转换为整型，后面会用到
        get_content(pages, title, url)

def get_content(pages, title, url):
    print('正在保存%s' % title)

    for page in range(1, pages + 1):
        if page == 1:
            link = url
        else:
            link = url[:-5] + '_{}'.format(page) + url[-5:]    #每一张图片的地址
        response = requests.get(link, headers=headers)
        response.encoding = response.apparent_encoding
        html = response.text
        content_pattern = re.compile('a target="_blank" class="down-btn" href=\'(.*?)\'',re.S)
        images = re.findall(content_pattern, html)
        save_content(images, title, link)


def save_content(image, title, link):
    path = r'D:/Python/xiaohua'
    folder_path = path + '/' + title

    try:
        if not os.path.exists(folder_path):    #检查文件夹是否存在
            os.mkdir(folder_path)
    except FileExistsError:
        return None
    os.chdir(folder_path)    #移到要保存的文件夹中

    for url in image:
        print('正在保存图片', url)
        content = requests.get(url, headers = {'Referer':link}).content    #图片的二进制格式，并且每张图片的Referer都是不一样的。
        file_path = '{0}\{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')    #用md5的方式检查如片是否重复
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:    #保存图片
                f.write(content)
                f.close()
        else:
            print('文件已经存在了！')




def spider(url):
        result = get_page_index(url)
        result = parse_page_index(result)


if __name__ == '__main__':
    url = ["http://www.mmonly.cc/tag/xh1/{}".format(page) + ".html" for page in ['index', '2', '3','4', '5', '6']]
    pool = Pool(6)
    pool.map(spider, url)	#开启多进程
    pool.close()
    pool.join()
