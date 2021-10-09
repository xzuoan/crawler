import requests
import redis
from bs4 import BeautifulSoup
import time
import os

'''
基于Redis断点续爬
仅爬取一页效果演示
'''

proxies = {'htttp':'http://{}'.format('101.200.127.14:3129'),
            'htttps':'https://{}'.format('101.200.127.14:3129')}
headers = {'Referer':'m.quantuwang1.com',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}

def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)

def push_Redis(r_link, pages, texts, count):

    r_link.rpush(f'{texts}', pages)
    print(f'{count}.写入{texts}{pages}')
    r_link.expire(f'{texts}', 360)

def get_Redis(r_link, keys):

    link = r_link.lpop(f'{keys}')
    return link

def main():
    url = 'http://m.quantuwang1.com/meinv/imiss/'
    headers = {'Host': 'm.quantuwang1.com',
               'Referer': 'https://www.baidu.com/',
               'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}

    response = BeautifulSoup(requests.get(url, headers=headers, proxies=proxies).content,'html.parser')
    # print(response)
    links = response.find('div', class_='index_middle_c').find_all('a')
    base = []
    for link in links:
        temp = {}
        temp['href'] = 'http://m.quantuwang1.com/' + link.get('href')
        temp['text'] = link.get_text()
        base.append(temp)
    return base

def push_link(base):
    r_link = redis.Redis(port='6379', host='localhost', decode_responses=True, db=1)
    for i in base:
        hrefs = i['href']
        texts = i['text']
        pic_response = BeautifulSoup(requests.get(url=hrefs, headers=headers, proxies=proxies).content, 'html.parser')
        time.sleep(1)
        pages = pic_response.find('div',class_='index_c_page').find_all('a')
        count = 1
        for i in pages:
            page = 'http://m.quantuwang1.com/' + i.get('href')
            push_Redis(r_link, page, texts, count)
            count += 1
    r_link.close()

def link_download(base):
    for i in base:
        r_link = redis.Redis(port='6379', host='localhost', decode_responses=True, db=1)
        texts = i['text']
        len = int(r_link.llen(f'{texts}'))
        while len:
            link = get_Redis(r_link, keys=texts)
            create_dir(r'pic\{}'.format(texts))
            print('======开始下载{}======'.format(texts))

            page_response = BeautifulSoup(requests.get(url=link, headers=headers, proxies=proxies).content, 'html.parser')
            pic_src = page_response.find('div', class_='index_c_img').find('img').get('src')

            headers1 = {'Referer': link,
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}
            src_response = requests.get(url=pic_src, headers=headers1,proxies=proxies).content

            with open(r'\pic\{}\{}'.format(texts, pic_src.split('/')[-1]), 'wb') as f:

                f.write(src_response)
            print('======{}download successed======'.format(pic_src.split('/')[-1]))
            len -= 1
        r_link.close()

if __name__=='__main__':
    base = main()
    push_link(base)           # 爬取链接存入redis
    r_link = redis.Redis(port='6379', host='localhost', decode_responses=True, db=1)
    lens = int(len(r_link.keys("*"))) - 1           # 读取存入键长
    r_link.close()
    while lens:
        link_download(base)
        lens -= 1
