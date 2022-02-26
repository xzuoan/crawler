# -*- coding=utf-8 -*-
import requests
import re
import os
from time import sleep
import threading
import asyncio


def create_folder(filename):
    if not os.path.exists(filename):
        os.makedirs(filename)
        print("创建文件夹成功：", os.path.abspath("pictures"))
        sleep(1)


def get_data_link(pattern, data):
    result = re.findall(pattern, data)
    if len(result) == 0:
        print(f"link：{data}\n匹配结果为空[pass]")
        raise IndexError
    else:
        return result


def downloader(num, link):
    filename = "pictures"
    create_folder(filename)
    try:
        response = session.get(link)
        if response.content and response.status_code == 200:
            with open(r"pictures/{}".format(str(link).split('/')[-1]), "wb") as f:
                f.write(response.content)
            print(f"{[num]}{str(link).split('/')[-1]}下载成功")
            sleep(0.5)
        else:return
    except Exception as e:
        print(f"{[num]}{str(link).split('/')[-1]}下载失败")
        print("error reason:", e)
        return


def fix_link(hrefs):
    lists = []
    for href in hrefs:
        if not str(href).startswith("http" or "https"):
            if not str(href)[0:33].split(".")[-1].startswith("com" or "cn" or "net" or 'cc') or str(href)[0:33].startswith(host):
                href = protocol + "/" + host + href
            else:
                href = protocol + href
            if not href[7:].startswith("/"):
                href = href[0:7] + "/" + href[7:]
        if not (str(href).endswith(".jpg") or str(href).endswith(".png")):
            href = href + ".jpg"
        if href in lists or (("qqonline" or "weixinqrcode" or "file" or "taobao" or '') in str(href)):
            continue
        lists.append(href)
        lists = list(set(lists))
    return lists


def access_link(link):
    try:
        try:
            return session.get(link, timeout=5).content.decode(encoding="utf8")
        except:
            return session.get(link, timeout=5).content.decode(encoding="gbk")
    except:return


class LinkFilter:

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36\
                                                        (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.35',
                        "sec-ch-ua-platform": "Windows"}
        self.pattern1 = 'href="(.*?)".*?src|src*="[a-zA-Z0-9\-\/\.\:\_]+.jpg"'                          # get href1
        # self.pattern2 = '\ssrc.*?="(.*?.jpg)" '                                                          # get src
        self.pattern2 = 'src="([a-zA-Z0-9\-\/\.\:\_]+.[jpg|png])"'                                             # get src
        self.pattern3 = '<a href="(.*?)>下一页</a>'                                                      # get next page1
        self.pattern4 = 'class="*next*".*?href="(.*?)"'                                                 # get next page2

    def get_menu_data(self, url):
        global session
        global protocol
        global host
        protocol = url.split("/")[0]
        host = url.split('/')[2]
        session = requests.session()
        session.get(url=url, headers=self.headers)
        try:
            return session.get(url=url, headers=self.headers, timeout=5).content.decode(encoding="utf8")
        except:
            return session.get(url=url, headers=self.headers, timeout=5).content.decode(encoding="gbk")

    def sift_link(self, result):
        links = []
        for href in result:
            if str(href).replace('//', '').startswith("wpa.qq.com") or \
                    str(href).endswith(".js" or ".css" or "#" or ";" or "@" or ":"):
                continue
            if not str(href).startswith(protocol):
                href = protocol + str(href)
                if not href[6:].startswith("/"):
                    href = href[0:6] + "/" + href[6:]
                lists = str(href).split("/")
                if host not in lists:
                    lists.insert(lists.index(protocol)+1, host)
                    href = "/".join(lists)
                    if not href[7:].startswith("/"):
                        href = href[0:7] + "/" + href[7:]
                    links.append(href)
                else:links.append(href)
            else:links.append(href)
        links = list(set(links))
        print(f"共匹配到{len(links)}个结果")
        return links

    def next_page(self, data):
        try:
            try:
                result = re.findall('href="(.*?)"', re.search(self.pattern3, data).group(1))[-1]
            except:
                result = re.search(self.pattern4, data).group(1)
            result = self.sift_link([result])
            return result
        except:return

    def img_download(self, url):
        data = self.get_menu_data(url)
        result = get_data_link(self.pattern1, data)
        if len(result) <= 8:
            pattern5 = f'href="(.*?{host}.*?.html)"'                                                       # get href2
            result = get_data_link(pattern5, data)
        links = self.sift_link(result)                                                                     # menu href
        img_links = []
        for link in links:
            img_data = access_link(link)
            if img_data:
                try:
                    hrefs = get_data_link(self.pattern2, img_data)
                    lists = fix_link(hrefs)
                    for href in lists:
                        img_links.append(href)
                except IndexError:pass
            else:continue
        if len(img_links) > 0:
            img_links = list(set(img_links))
            print(f"共匹配到{len(img_links)}条链接")
            for num, link in enumerate(img_links, 1):
                downloader(num, link)
        return data

    def main(self, url):
        data = self.img_download(url)
        try:
            next_page = self.next_page(data)[0]
            print("next page：", next_page)
            if input("检测到可翻页，是否翻页下载?<y or n>").lower() in ["y", "yes"]:
                while next_page:
                    datas = self.img_download(url=next_page)
                    next_page = self.next_page(datas)[0]
                    print(next_page)
            print("下载结束")
        except:pass


def threading_download():
    urls = ['https://pic.netbian.com/4kmeinv/', 'https://www.mmlme.com/',]
    threads = []
    for url in urls:
        threads.append(threading.Thread(target=LinkFilter().main, args=(url,)))
    for thread in threads:
        # thread.setDaemon(True)
        thread.start()


def async_download():
    urls = ['https://pic.netbian.com/4kmeinv/', 'https://www.mmlme.com/',]
    tasks = [LinkFilter().main(url) for url in urls]
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(asyncio.gather(*tasks))
    event_loop.close()


if __name__ == '__main__':
    target_thread = False
    target_async = False
    if target_thread is True:                                                                                # 启用线程池
        threading_download()
    elif target_async is True:
        async_download()
    else:
        # url = "https://pic.netbian.com/4kmeinv/"                                                               # √
        # url = "https://www.mmonly.cc/gqbz/"
        # url = 'https://wallhaven.cc/search?q=id:5&sorting=random&ref=fp'                                       # √
        d = LinkFilter()
        d.main(url)
