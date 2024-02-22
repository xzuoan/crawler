# -*- encoding=utf-8 -*-

import math
import random
import requests
from urllib import parse
import json
import time
import re

'''
created on 2024-01-11
updated on 2024-02-14
'''

# request links
HOST = 'www.kuwo.cn'
HOMEPAGE = 'https://www.kuwo.cn'
KEYWORD_SEARCH_PAGE = 'https://www.kuwo.cn/search/list?key='
API_SEARCH_MUSIC_BY_KEYWORD = 'https://www.kuwo.cn/search/searchMusicBykeyWord'

# default params
# default_Hm_Iuvt = 'Hm_Iuvt_cdb524f42f0cer9b268e4v7y735ewrq2324'
default_Hm_Iuvt = 'Hm_Iuvt_cdb524f42f23cer9b268564v7y735ewrq2324'  # 更新 2024-02-21
default_Hm_lvt = 'Hm_lvt_cdb524f42f0ce19b169a8071123a4797'
default_Hm_lpvt = 'Hm_lpvt_cdb524f42f0ce19b169a8071123a4797'


# 从cookie响应中提取关键参数
def get_HmIuvt_from_cookie(coo: str):
    split_list = coo.split(';')
    for sl in split_list:
        try:
            return re.search("Hm_Iuvt[\\w]+=([a-zA-Z0-9]+)", sl).group()
        except:
            continue
    else:
        raise Exception(AttributeError, "请求响应的cookie中找不到需要的Hm_Iuvt值")


# 复现JS中parseInt()方法，规则：1.正常数字类型同int()方法 2.字符串中含特殊任何非数字类型从该处截取 3.排除字符串前后空格
def parseInt(num: str) -> int:
    num = str(num).strip()
    n = ""
    for i in num:
        if i.isdigit():
            n += i
        else:
            break
    return int(n)


# e ="Hm_Iuvt_cdb524f42f0cer9b268e4v7y735ewrq2324"
# t = "znrjrRB6E74WN7nN8NS2w46tfdJpyhb8"
# secret加密方法
def get_secret(t, e):
    if e is None or len(e) <= 0:
        pass  # raise error
    n, i = "", 0
    while i < len(e):
        n += str(ord(str(e)[i]))
        i += 1
    r = math.floor(len(n) / 5)
    # 2024-02-21 原来e的长度从43改到45，python运行n[5 * r]会超出索引报错，但在JS中n.charAt(5 * r)超出索引结果为0
    # o = int(n[r] + n[2 * r] + n[3 * r] + n[4 * r] + n[5 * r])
    o = int(n[r] + n[2 * r] + n[3 * r] + n[4 * r])
    l = math.ceil(len(e) / 2)
    c = int(math.pow(2, 31)) - 1

    if o < 2:
        pass  # raise error
    d = int(round(1e9 * random.random()) % 1e8)

    # "for (n += d; n.length > 10; )"
    n = f"{n}{d}"
    while len(str(n)) > 10:
        # 踩坑：JS在展示较长精度数字时n自动转换为科学计数法显示类型，当n.toString后变成长度20（原110）的字符串类型
        n = parseInt(str(n)[0: 10]) + parseInt(str(n)[10: len(str(n))])
        # "1.7118116959910099e+102"
        # "1.71181169599101e+99"
        # "1.2345678901234568e+21"
        if len(str(n)) > 21:
            n = "%.16e" % n
    n = (o * int(n) + l) % c

    f, h = "", 0
    i_ = 0
    while i_ < len(t):
        h = int(ord(str(t)[i_]) ^ math.floor(n / c * 255))
        f += "0" + format(int(hex(int(h)), 16), 'x') if h < 16 else format(int(hex(int(h)), 16), 'x')
        n = (o * int(n) + l) % c
        i_ += 1
    d = format(int(hex(int(d)), 16), 'x')
    while len(d) < 8:
        d = "0" + d
    return f + d


# proxy_pool = [
#     {"http": "http://5.161.66.223:8080", "https": "https://5.161.66.223:8080"},
#     {"http": "http://188.209.250.228:8080", "https": "https://188.209.250.228:8080"},
#     {"http": "http://134.35.15.253:8080", "https": "https://134.35.15.253:8080"},
#     {"http": "http://183.89.66.121:8080", "https": "https://183.89.66.121:8080"},
#     {"http": "http://94.130.70.172:8080", "https": "https://94.130.70.172:8080"},
#     {"http": "http://23.152.40.14:3128", "https": "https://23.152.40.14:3128"},
# ]


class KWMusic:

    def __init__(self):
        self.total = 0
        # self.proxy = random.choice(proxy_pool)
        self.proxy = None

        # 首次访问的默认请求头参数
        self.request_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Host': HOST,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.request_header_APP_UA = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.1; OPPO R9sk) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/76.0.3809.111 Mobile Safari/537.36"
        }

        self.search_music_params = {
            'vipver': '1',
            'client': 'kt',
            'ft': 'music',
            'cluster': '0',
            'strategy': '2012',
            'encoding': 'utf8',
            'rformat': 'json',
            'mobi': '1',
            'issubtitle': '1',
            'show_copyright_off': '1',
            'pn': '',       # 页数
            'rn': '20',     # 单页展示总数
            'all': ''       # 搜索内容
        }

        self.timestamp = int(time.time())
        self.Hm_Iuvt = None

    # 首页只需要访问一次，目的在于拿到第一个Hm_Iuvt
    def search_page(self, keyword):

        search_page_url = KEYWORD_SEARCH_PAGE + parse.quote(keyword)
        search_page_resp = requests.get(url=search_page_url, headers=self.request_header, proxies=self.proxy)
        return get_HmIuvt_from_cookie(search_page_resp.headers["Set-Cookie"])

    def kw_search(self, keyword, pn=0) -> list:

        if pn < 0: pn = 0
        # 首次请求获取Hm_Iuvt
        if not (self.Hm_Iuvt and pn):
            self.Hm_Iuvt = self.search_page(keyword)
        # 设置Cookie
        cookie_extra = f"{default_Hm_lvt}={self.timestamp}; " \
                       f"{default_Hm_lpvt}={self.timestamp}; " \
                       f"{self.Hm_Iuvt}"
        self.request_header.update({
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': KEYWORD_SEARCH_PAGE + parse.quote(keyword),
            'Cookie': cookie_extra
        })
        self.search_music_params.update({"all": keyword, "pn": str(pn)})
        search_music_page_resp = requests.get(url=API_SEARCH_MUSIC_BY_KEYWORD, headers=self.request_header,
                                              params=self.search_music_params, proxies=self.proxy)
        # 更新Hm_Iuvt
        self.Hm_Iuvt = get_HmIuvt_from_cookie(search_music_page_resp.headers["Set-Cookie"])
        # 获取 reqId
        search_music_page_info = json.loads(search_music_page_resp.content)
        self.reqId = search_music_page_info.get('UK')
        if not pn:
            self.total = search_music_page_info.get('TOTAL')
        # reqId = reqId[0:8] + '-' + reqId[8:12] + '-' + reqId[12:16] + '-' + reqId[16:20] + '-' + reqId[20:]
        # reqId = 'b4274401-a377-11eb-a99d-ef0323beeee3'
        # 数据清洗
        resp_music_info_list = search_music_page_info['abslist']
        music_info_list = []
        for info in resp_music_info_list:
            music_info_list.append({'album': info['ALBUM'], 'artist': info['ARTIST'],
                                    'seed': info['DC_TARGETID'], 'name': info['SONGNAME']})
        return music_info_list

    def __update_headers(self, rid):
        # 设置Cookie
        now_timestamp = int(time.time())
        cookie_extra = f"{default_Hm_lvt}={self.timestamp}; " \
                       f"{default_Hm_lpvt}={now_timestamp}; " \
                       f"{self.Hm_Iuvt}; " \
                       f"_ga=GA1.2.454541416.{now_timestamp}; " \
                       f"_gid=GA1.2.49392487.{now_timestamp}"
        e, t = self.Hm_Iuvt.split("=")
        encrypt_secret = get_secret(t, e)
        self.request_header.update({
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'http://kuwo.cn/play_detail/{rid}',
            'Cookie': cookie_extra,
            'Secret': encrypt_secret
        })

    # 获取歌曲下载链接
    def kw_get_play_url(self, rid):

        # url = 'http://kuwo.cn/url'
        # params = {
        #     'format': 'mp3',
        #     'rid': rid,
        #     'response': 'url',
        #     'type': 'convert_url3',
        #     'br': '320kmp3',
        #     'from': 'web',
        #     't': int(float('%.3f' % time.time())*1000),
        #     'httpsStatus': 1,
        #     'reqId': reqId
        # }
        url = 'http://kuwo.cn/api/v1/www/music/playUrl'
        params = {
            'plat': 'web_www',
            'mid': rid,
            'type': 'music',
            # 'br': '320kmp3',
            'br': '192kmp3',
            # 'br': '128kmp3',
            'from': '',
            'httpsStatus': 1,
            'reqId': self.reqId
        }
        self.__update_headers(rid)
        access_music_resource_resp = requests.get(url, headers=self.request_header, params=params, proxies=self.proxy)
        return json.loads(access_music_resource_resp.content)

    def kw_get_music_info(self, rid):
        url = "http://kuwo.cn/api/www/music/musicInfo"
        params = {
            "mid": rid,
            "httpsStatus": 1,
            "reqId": self.reqId,
            "plat": "web_www",
            "from": ""
        }
        self.__update_headers(rid)
        access_music_info_resp = requests.get(url, headers=self.request_header, params=params, proxies=self.proxy)
        music_info_data = json.loads(access_music_info_resp.content)["data"]
        return music_info_data["songTimeMinutes"], music_info_data["releaseDate"], music_info_data["albumpic"]


# if __name__ == '__main__':
#     kw = KWMusic()
    # data = kw.kw_search("test")
    # print(kw.kw_get_play_url(data[0]["seed"]))
    # print(kw.kw_get_music_info(data[0]["seed"]))

