'''
torrent爬虫工具
'''
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import threading

class Zooqle:
    
    def __init__(self, keywords):
        self.url = f'https://zooqle.com/search?pg=1&q={keywords}&v=t&s=ns&sd=d'
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.1"}
    
    def get_response(self):
        try:
            response = requests.get(self.url, self.headers, timeout=5).text
            return response
        except:
            return 0

    def parse_response(self, response):
        try:
            pattern = re.compile('<a class=" small" href="/(?P<p>.*?)">(.*?)</a><div class="text-nowrap"', re.S)
            magnet = re.compile('<a title="Magnet link" rel="nofollow" href=(?P<m>.*?)<i class="spr dl-magnet">', re.S)
            title = pattern.finditer(response)
            magnets = magnet.finditer(response)
            for i, j in zip(title, magnets):
                print(i.group('p'), '\n', j.group('m'))
        except:
            print('Null')       
    
    def main(self):
        print('-'*50, 'zooqle', '-'*50)
        response = self.get_response()
        self.parse_response(response)

class Kickasstorrent:

    def __init__(self, keywords):
        self.url = f'https://kickasstorrent.cr/search/{keywords}/1/?sortby=seeders&sort=desc'
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.1"}

    def get_response(self):
        response = requests.get(self.url, self.headers).text
        return response

    def parse_response(self, response):
        html = BeautifulSoup(response, 'html.parser')
        # nodes = html.find('table', class_="data frontPageWidget").find_all(re.compile('^tr'))[1:]
        try:
            nodes = html.find('table', class_="data frontPageWidget").find_all('tr', class_=["even", "odd"])
            for node in nodes:
                href ='https://kickasstorrent.cr' +  node.find('div', class_="torrentname").find_next('a').get('href')
                text = node.find('div', class_="torrentname").find('div').find('a').get_text()
                magnet = self.get_magnet(href)
                infos = []
                info = node.find_all('td', class_=['nobr center', 'center', 'green center', 'red lasttd center'])
                for i in info:
                    infos.append(i.get_text().strip())
                print(text, '\n',infos)     
                print(magnet)
        except:
            print('Null')        

    def get_magnet(self, href):
        try:
            response = requests.get(href, headers=self.headers).text
        except Exception as e:
            print(e)
            return 0
        html = BeautifulSoup(response, 'html.parser')
        magnet = html.find('div', id='tab-technical').find('div', class_="sharingWidgetBox").find('a').get('href')
        return magnet

    def main(self):
        print('-'*50, 'kickasstorrent', '-'*50)
        response = self.get_response()
        self.parse_response(response)

class Torrentgalaxy:

    def __init__(self, keywords):
        self.url = f'https://torrentgalaxy.to/torrents.php?search={keywords}&sort=seeders&order=desc&page=0'
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.1"}

    def get_response(self):
        response = requests.get(self.url, self.headers).text
        return response

    def parse_response(self, response, staus = False):
        html = etree.HTML(response)
        try:
            nodes = html.xpath('//*/div[@class="tgxtablerow txlight"]')
            staus = True
        except Exception as e:
            print(e)
            result = html.xpath('//*[@id="panelmain"]/div[2]/center/b/text()')[0]
            print(result)
        if staus:
            for node in nodes:
                text = node.xpath('./div[@id="click"]/div/a/b/text()')[0]
                magnet = node.xpath('./div[5]/a[2]/@href')[0]
                type = node.xpath('./div[1]/a/small/text()')[0].replace('&nbsp: ', ':')
                size = node.xpath('./div[8]/span/text()')[0]
                date = node.xpath('./div[12]/small/text()')[0]
                print(text, '\n',[type, size, date])
                print(magnet, '\n')

    def main(self):
        print('-'*50, 'torrentgalaxy', '-'*50)
        response = self.get_response()
        self.parse_response(response)        

class Torrentzeu:

    def __init__(self, keywords):
        self.url = f'https://torrentzeu.org/kick.php?q={keywords}&page=1'
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.1"}

    def get_response(self):
        response = requests.get(url=self.url, headers=self.headers)
        if response.status_code < 400:
            return response.text
        else:
            return 0

    def parse_response(self, response):
        if response:
            html = etree.HTML(response)
            try:
                nodes = html.xpath('//*[@id="table"]/tbody/tr')
            except:
                print('Null')
            for node in nodes:
                text = node.xpath('./td[1]/span/text()')[0]
                size = node.xpath('./td[5]/text()')[0]
                seeds = node.xpath('./td[3]/text()|./td[4]/text()')[0]
                date = node.xpath('./td[2]/text()')[0]
                magnet = node.xpath('./td[6]/a/@href')[0]
                print(text, '\n',[size, seeds, date])
                print(magnet, '\n')
        else:
            print('ConnectError')        

    def main(self):
        print('-'*50, 'torrentzeu', '-'*50)
        response = self.get_response()
        self.parse_response(response)

def run(keywords):
    zq = Zooqle(keywords)
    kt = Kickasstorrent(keywords)
    tg = Torrentgalaxy(keywords)
    tz = Torrentzeu(keywords)    
    thread = [threading.Thread(target=zq.main()), threading.Thread(target=kt.main()),
                threading.Thread(target=tg.main()), threading.Thread(target=tz.main())]
    for t in thread:
        t.setDaemon(True)
        t.start()


if __name__=="__main__":
    keywords = input('输入需要搜索的内容：')
    run(keywords)