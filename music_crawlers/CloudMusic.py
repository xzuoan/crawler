#coding=utf-8
import requests
import json
import base64
import random
import time
from Crypto.Cipher import AES
import codecs
import pandas
import os
from contextlib import closing


Tu8m_emj = {
        "色": "00e0b",
        "流感": "509f6",
        "这边": "259df",
        "弱": "8642d",
        "嘴唇": "bc356",
        "亲": "62901",
        "开心": "477df",
        "呲牙": "22677",
        "憨笑": "ec152",
        "猫": "b5ff6",
        "皱眉": "8ace6",
        "幽灵": "15bb7",
        "蛋糕": "b7251",
        "发怒": "52b3a",
        "大哭": "b17a8",
        "兔子": "76aea",
        "星星": "8a5aa",
        "钟情": "76d2e",
        "牵手": "41762",
        "公鸡": "9ec4e",
        "爱意": "e341f",
        "禁止": "56135",
        "狗": "fccf6",
        "亲亲": "95280",
        "叉": "104e0",
        "礼物": "312ec",
        "晕": "bda92",
        "呆": "557c9",
        "生病": "38701",
        "钻石": "14af6",
        "拜": "c9d05",
        "怒": "c4f7f",
        "示爱": "0c368",
        "汗": "5b7a4",
        "小鸡": "6bee2",
        "痛苦": "55932",
        "撇嘴": "575cc",
        "惶恐": "e10b4",
        "口罩": "24d81",
        "吐舌": "3cfe4",
        "心碎": "875d3",
        "生气": "e8204",
        "可爱": "7b97d",
        "鬼脸": "def52",
        "跳舞": "741d5",
        "男孩": "46b8e",
        "奸笑": "289dc",
        "猪": "6935b",
        "圈": "3ece0",
        "便便": "462db",
        "外星": "0a22b",
        "圣诞": "8e7",
        "流泪": "01000",
        "强": "1",
        "爱心": "0CoJU",
        "女孩": "m6Qyw",
        "惊恐": "8W8ju",
        "大笑": "d"
    }
Tu8m_md = ["色", "流感", "这边", "弱", "嘴唇", "亲", "开心", "呲牙", "憨笑", "猫", "皱眉", "幽灵", "蛋糕", "发怒", "大哭", "兔子", "星星", "钟情", "牵手", "公鸡", "爱意", "禁止", "狗", "亲亲", "叉", "礼物", "晕", "呆", "生病", "钻石", "拜", "怒", "示爱", "汗", "小鸡", "痛苦", "撇嘴", "惶恐", "口罩", "吐舌", "心碎", "生气", "可爱", "鬼脸", "跳舞", "男孩", "奸笑", "猪", "圈", "便便", "外星", "圣诞"]

# param2&param2&param4实际为固定值，可以省略函数构造
# param2 = "010001"
# param3 = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
# param4 = "0CoJUm6Qyw8W8jud"

def search():
    status = 1
    keyword = input('输入要搜索的关键词：')
    if keyword =='':
        print('输入内容不能为空')
        search()
    else:
        type = input('输入要搜索的类型:\n<单曲 专辑 歌手 歌单 用户 mv 歌词 主播电台>').strip()
        while status:
            if type =='单曲':
                type = 1
            elif type == '专辑':
                type = 10
            elif type == '歌手':
                type = 100
            elif type == '歌单':
                type = 1000
            elif type == '用户':
                type = 1002
            elif type == 'mv':
                type = 1004
            elif type == '歌词':
                type = 1006
            elif type == '主播电台':
                type = 1009
            if type in [1,10,100,1000,1002,1004,1006,1009]:
                status = 0
            else:
                type = input('输入要搜索的类型:\n<单曲 专辑 歌手 歌单 用户 mv 歌词 主播电台>')
        return keyword, type

def get_bqN1x(md):
    m0x = []
    for key in md:
        m0x.append(Tu8m_emj[key])
    return m0x
param2 = "".join(get_bqN1x(["流泪","强"]))                      # encSecKey key
param3 = "".join(get_bqN1x(Tu8m_md))                            # c
param4 = "".join(get_bqN1x(["爱心", "女孩", "惊恐", "大笑"]))  #  h_encText key

def AES_encrypt(text, key):
    '''
    text为密文，key为公钥，iv 为偏移量
    js逆向破解方法引自https://blog.csdn.net/weixin_40352715/article/details/107879915
    '''
    iv = b"0102030405060708"
    pad = 16 - len(text) % 16
    text += pad * chr(pad)
    text = text.encode('utf-8')
    encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text.decode('utf-8')

def RSA_encrypt(text, key, modulus):
    text=text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(key, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)       # 返回encseckey字节长度为256byte

def asrsea(p1, p2, p3, p4):
    res = {}
    rand_num = "".join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for i in range(16)])   
    h_encText = AES_encrypt(p1, p4)
    h_encText = AES_encrypt(h_encText, rand_num)
    res["encText"] = h_encText
    res["encSecKey"] = RSA_encrypt(rand_num, p2, p3)
    return res

def search_result(keyword, type):
    param1 = json.dumps({"csrf_token": "","hlposttag": "</span>","hlpretag": "<span class='s-fc7'>","limit": "30","offset": "0","s": keyword,"total": "true","type": type})

    asrsea_res = asrsea(param1, param2, param3, param4)

    url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.35 ",
                "Referer": "https://music.163.com/search/"
    }

    param_data = {"params": asrsea_res["encText"],
                    "encSecKey": asrsea_res["encSecKey"]}

    r = json.loads(requests.post(url, headers=headers, data=param_data).text)
    # print(param_data)
    songcount = r['result']['songCount']
    songs = r['result']['songs']
    list = []
    for song in songs:
        result = {}
        result['name'] = song['name']
        result['id'] = song['id']
        result['singer'] = song['ar'][0]['name']
        result['album'] = song['al']['name']
        result['times'] = '%02d:%02d' % (song['dt']//(60*1000), song['dt'] % (60*1000)//1000)
        list.append(result)
    info = pandas.DataFrame(list, index=[i for i in range(1, songcount + 1)])
    # pandas.set_option('display.max_columns', 1000)                  # 设置显示最大列数
    # pandas.set_option('display.width', 1000)                        # 显示宽度
    # pandas.set_option('display.max_colwidth', 500)                 # 最大列数
    pandas.set_option('display.unicode.ambiguous_as_wide', True)    #
    pandas.set_option('display.unicode.east_asian_width', True)      # 列名对齐
    pandas.set_option('colheader_justify', 'center')                 # 中心对齐，left，right，center
    print(f'搜索到{songcount}条结果')
    print('='*150)
    print(info)
    print('='*150)
    return list

def ask_download(list, number):
    name = list[number - 1]['name']
    id = list[number - 1]['id']
    singer = list[number - 1]['singer']
    param5 = json.dumps({"csrf_token": "", "ids": f"[{id}]", "br": 320000})       # 默认请求最大音质为320K，实际以服务器给定为准
    asrsea_res = asrsea(param5, param2, param3, param4)
    param_data = {"params": asrsea_res["encText"],
                "encSecKey": asrsea_res["encSecKey"]}
    url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.35",
               "Referer": "https://music.163.com/"}
    try:
        r = json.loads(requests.post(url, headers=headers, data=param_data).text)
    except Exception as e:
        print('Error:', e)
    src = r['data'][0]['url']
    br = int(r['data'][0]['br']/1000)
    size = '%2d' % (r['data'][0]['size']/1024/1024)
    print('[{}]开始下载<{}>, 音质{}K, 大小{}MB'.format(time.strftime("%H:%M:%S", time.localtime()), name, br, size))
    try:
        downlaoder(src, name=name, singer=singer)
        print('\n[{}]下载完成'.format(time.strftime("%H:%M:%S", time.localtime())))
    except Exception as e:
        print('[{}]下载失败'.format(time.strftime("%H:%M:%S", time.localtime())))
        print('Error:', e)

def downlaoder(url, name, singer):
    folder = 'cloudmusic'
    if not os.path.exists(folder):
        os.makedirs(folder)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.35"}

    with closing(requests.get(url, headers=headers, stream=True)) as r:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(r.headers['content-length'])  # 文件总大小
        data_count = 0 # 当前已传输的大小
        with open(r'cloudmusic\{}-{}.mp3'.format(singer, name), 'wb')as f:
            for data in r.iter_content(chunk_size=chunk_size):
                f.write(data)
                done_block = int((data_count / content_size) * 50)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r %s：[%s%s] %d%%" % (name, done_block * '█', ' ' * (50 - 1 - done_block), now_jd), end=" ")

def selecter(list):
    staus = 1
    number = int(input('输入要下载的序号 <1-20>'))
    while staus:    
        if number in range(1, 21):
            ask_download(list, number)
            staus = 0
        else:
            print('请重新输入正确的序号')
            number = int(input('输入要下载的序号 <1-20>'))

def main():
    keyword, type = search()
    list = search_result(keyword, type)
    if input('是否选择下载？ <Yes or No>').lower() in ['y','yes']:
        selecter(list)
    else:
        print('SEARCH END')
    staus = 1
    while staus:
        if input('是否继续下载？ <Yes or No>').lower() in ['y','yes']:
            selecter(list)
        else:
            staus = 0
            print('USE END')
if __name__=="__main__":
    main()