import os
import shutil
import time
import threading
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

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

imgurl_lst = []


# 下载图片
def download_img(img_url, img_localpath):
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(img_localpath, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


# 爬取详情页
def craw_detail(url):
    print(f'{threading.current_thread().name} >>> 正在执行')
    # 网页前缀
    url_prefix = 'http://pic.netbian.com'
    # 获取网页
    content = requests.get(url)
    # 设置编码
    content.encoding = 'gbk'
    # 解码
    content = content.text

    soup = BeautifulSoup(content, 'lxml')

    for div in soup.find_all('div', class_='slist'):
        # print([img.get('src') for img in div.find_all('img') if img.get('src')])
        new_lst = [url_prefix + img.get('src') for img in div.find_all('img') if img.get('src')]

    return new_lst


# 下载图片
def download(imgurl):
    print(f'{threading.current_thread().name} >>> 正在执行')

    if not os.path.exists('./netbian'):
        os.mkdir('./netbian')

    dir = os.path.abspath('./netbian')
    filename = os.path.basename(imgurl)
    imgpath = os.path.join(dir, filename)
    download_img(imgurl, imgpath)


def run(start_page, end_page):
    with ThreadPoolExecutor(max_workers=8) as t:
        begin = time.time()
        obj_lst = []
        for i in range(start_page, end_page + 1):
            if i == 1:
                page_url = 'http://pic.netbian.com/index.html'
            else:
                page_url = f'http://pic.netbian.com/index_{i}.html'

            obj = t.submit(craw_detail, page_url)
            obj_lst.append(obj)
        for future in as_completed(obj_lst):
            data = future.result()
            # print(data)
            imgurl_lst.extend(data)
        print(imgurl_lst)
        print(len(imgurl_lst))
        print(f'耗时：{time.time() - begin}')

        begin = time.time()
        for imgurl in imgurl_lst:
            obj = t.submit(download, imgurl)
            obj_lst.append(obj)

        for future in as_completed(obj_lst):
            data = future.result()
        print(f'耗时：{time.time() - begin}')


if __name__ == '__main__':
    run(1, 10)
