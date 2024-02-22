import math
import requests
from urllib import parse
import json
import time
import pandas
from contextlib import closing
import os

# 输入搜索内容keyword，(list{单曲}，album{专辑}，mv{MV}, playlist{歌单}， singers{歌手})
def search():
    status = 1
    keyword = str(input('输入要搜索的关键词：').strip())
    if keyword =='':
        print('输入内容不能为空')
        search()
    else:
        type = str(input('输入要搜索的类型:\n<单曲 专辑 歌手 歌单 mv>').strip())
        while status:
            if type =='单曲': type = "list" 
            elif type == '专辑':  type = "album"              
            elif type == '歌手': type = "singers"               
            elif type == '歌单': type = "playlist"               
            elif type == 'MV': type = "mv"                
            if type in ["list", "album", "singers", "playlist", "mv"]:
                status = 0
            else:
                type = input('输入要搜索的类型:\n<单曲 专辑 歌手 歌单 mv>')
        return keyword, type

# 访问search首页拿到csrf
def search_list(keyword, type):
    url = f'http://kuwo.cn/search/{type}'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.35 "}
    data = {'key': keyword}
    response = requests.get(url, headers=headers, params=data)
    csrf = response.headers['Set-Cookie'].split(';')[0].split('=')[-1]
    return csrf   

def search_result(csrf, keyword, page_number):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'csrf': csrf,
        "Cookie": f"kw_token={csrf}",
        'Referer': f'http://kuwo.cn/search/list?key={parse.quote(keyword)}'}
    data = {
        'key':keyword,
        'pn': page_number,
        'rn': 30,
        'httpsStatus':1}
        # 'reqId': '38a7543f-948a-8873-84d3-88ee74856ad5'}
    url = 'http://kuwo.cn/api/www/search/searchMusicBykeyWord'
    # url = 'http://kuwo.cn/api/www/search/searchMusicBykeyWord?key=%E5%AD%99%E7%87%95%E5%A7%BF&pn=1&rn=30&httpsStatus=1&reqId=94a12450-206f-11ec-8ef7-ebcd12d6dbf8'
    try:
        r = requests.get(url, headers=headers, params=data)
    except Exception as e:
        print('Error:', e)
    response = json.loads(r.text)
    search_csrf = r.headers['Set-Cookie'].split(';')[0].split('=')[-1]
    return response, search_csrf

def reslut_parse(response, count):
    songs = response['data']['list']
    list = []
    for song in songs:
        result = {}
        result['name'] = song['name']                   # 曲名
        result['id'] = song['rid']                      # 曲id
        result['singer'] = song['artist']               # 歌手
        result['album'] = song['album']                 # 专辑
        result['times'] = song['songTimeMinutes']       # 时长
        list.append(result)
    frame = pandas.DataFrame(list, index=[i for i in range((count-1)*30 + 1, (count-1)*30 + len(list) + 1)])
    pandas.set_option('display.unicode.ambiguous_as_wide', True)
    pandas.set_option('display.unicode.east_asian_width', True)
    pandas.set_option('colheader_justify', 'center')
    print('='*150)
    print(frame)
    print('='*150)
    return list

def ask_pageturning(response, page_number, pages, search_csrf, keyword):
    Lists = []
    list = reslut_parse(response, count=page_number)
    Lists.append(list)
    if pages > 1:
        staus = 1
        count = 2
        while staus:
            if input('是否翻页？<yes or no >') in ['yes', 'y']:
                list =  reslut_parse(search_result(csrf=search_csrf, keyword=keyword, page_number=count)[0], count=count)
                Lists.append(list)
                count += 1
            else:
                staus = 0
    return Lists

def selecter(Lists, reqid, csrf, keyword):
    staus = 1
    number = int(input('输入要下载的序号：'))
    while staus:    
        if number in range(1, len(Lists)*30 + 1):
            ask_download(Lists, number, reqid, csrf, keyword)
            staus = 0
        else:
            print('请重新输入正确的序号')
            number = int(input('输入要下载的序号：'))

def ask_download(Lists, number, reqid, csrf, keyword):
    timestamp = int(float('%.3f' % time.time())*1000)
    rid = Lists[math.ceil(number/30) - 1][(number - (math.ceil(number/30) - 1)*30) - 1]['id']
    name = Lists[math.ceil(number/30) - 1][(number - (math.ceil(number/30) - 1)*30) - 1]['name']
    singer = Lists[math.ceil(number/30) - 1][(number - (math.ceil(number/30) - 1)*30) - 1]['singer']
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'csrf': csrf,
        "Cookie": f"kw_token={csrf}",
        'Referer': f'http://kuwo.cn/search/list?key={parse.quote(keyword)}'
    }
    url = 'http://kuwo.cn/url'
    data = {
            'format': 'mp3',
            'rid': rid,
            'response': 'url',
            'type': 'convert_url3',
            'br': '320kmp3',
            'from': 'web',
            't': timestamp,
            'httpsStatus': 1,
            'reqId': reqid
    }
    try:
        response = json.loads(requests.get(url, headers=headers, params=data).text)
        src = response['url']
    except Exception as e:
        print('Error:', e)
    try:
        downlaoder(src, name=name, singer=singer)
        print('\n[{}]下载完成'.format(time.strftime("%H:%M:%S", time.localtime())))
    except Exception as e:
        print('[{}]下载失败'.format(time.strftime("%H:%M:%S", time.localtime())))
        print('Error:', e)

def downlaoder(url, name, singer):
    folder = 'Kuwo_music'
    if not os.path.exists(folder):
        os.makedirs(folder)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.35"}

    with closing(requests.get(url, headers=headers, stream=True)) as r:
        content_size = int(r.headers['content-length'])  # 文件总大小
        size ='%.1f' % (int(content_size)/1024/1024)
        print('[{}]开始下载<{}-{}.mp3>, 大小{}MB'.format(time.strftime("%H:%M:%S", time.localtime()), singer, name, size))
        data_count = 0 # 当前已传输的大小
        with open(r'Kuwo_music\{}-{}.mp3'.format(singer, name), 'wb')as f:
            for data in r.iter_content(chunk_size=1024):
                f.write(data)
                done_block = int((data_count / content_size) * 50)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r %s：[%s%s] %d%%" % (name, done_block * '█', ' ' * (50 - 1 - done_block), now_jd), end=" ")

def main():
    keyword, type = search()
    csrf = search_list(keyword, type)
    page_number = 1
    response, search_csrf = search_result(csrf, keyword, page_number)
    reqid = response['reqId'][0:8] + '-' + response['reqId'][8:12] + '-' + response['reqId'][12:16] + '-' + response['reqId'][16:20] + '-' + response['reqId'][20:]
    total = response['data']['total']
    pages = int(total)//30
    print(f'搜索到{total}条结果，共{pages}页')
    time.sleep(1)
    Lists = ask_pageturning(response, page_number, pages, search_csrf, keyword)
    if input('是否选择下载？ <Yes or No>').lower() in ['y','yes']:
        selecter(Lists, reqid, csrf, keyword)
    else:
        print('SEARCH END')
    staus = 1
    while staus:
        if input('是否继续下载？ <Yes or No>').lower() in ['y','yes']:
            selecter(Lists, reqid, csrf, keyword)
        else:
            staus = 0
            print('USE END')

if __name__=="__main__":
    main()