import os
import shutil
import threading

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "close",
    "Cookie": "_gauges_unique_hour=1; _gauges_unique_day=1; _gauges_unique_month=1; _gauges_unique_year=1; _gauges_unique=1",
    "Referer": "http://www.infoq.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER"
}

# 图片地址列表
url_lst = []


# 下载图片
def download_jpg(image_url, image_localpath):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(image_localpath, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


# 爬取详情页
def craw(url):
    print(f'{threading.current_thread().name} >>> 开始启动')

    content = requests.get(url, headers=headers).text

    soup = BeautifulSoup(content, 'lxml')

    for div in soup.find_all('div', class_='Left_bar'):
        lst = [url.get('href') for url in div.find_all('a') if url.get('href')]
    url_lst.extend(lst)

    print(f'{threading.current_thread().name} >>> 已经结束')


# 爬取图片
def craw2(url):
    print(f'{threading.current_thread().name} >>> 开始启动')

    content = requests.get(url, headers=headers).text

    soup = BeautifulSoup(content, 'lxml')

    if not os.path.exists('./win4000'):
        os.mkdir('./win4000')

    for div in soup.find_all('div', class_='pic-meinv'):
        for img in div.find_all('img', class_='pic-large'):
            imgurl = img.get('src')
            dir = os.path.abspath('./win4000')
            filename = os.path.basename(imgurl)
            imgpath = os.path.join(dir, filename)
            download_jpg(imgurl, imgpath)

    print(f'{threading.current_thread().name} >>> 已经结束')


for i in range(1, 6):
    print(f'开始爬取第 {i} 页')
    url = f'http://www.win4000.com/zt/yingxionglianmeng_{i}.html'
    craw(url)
    # t = threading.Thread(target=craw, args=(url,))
    # t.start()
    # t.join()
    print(f'完成爬取第 {i} 页')

print('开始下载图片')

for url in url_lst:
    t = threading.Thread(target=craw2, args=(url,))
    t.start()

print('图片下载完成')
