# -*- coding=utf-8 -*-
import math
import random
import hashlib
import base64
from urllib import parse
import json
from os import path, makedirs, chdir
import time
import requests
import re
from datetime import datetime
from contextlib import closing

keyword = input("Enter Keyword: ").strip()
url = f"https://www.kugou.com/yy/html/search.html#searchType=song&searchKeyWord={parse.quote(keyword)}"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh",
    "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

session = requests.Session()
session.headers.update(headers)
session.get(url)


def read_source_data(filename):
    abspath = path.join(path.dirname(path.dirname(__file__)), "source", filename)
    with open(abspath, "r", encoding="utf-8") as f:
        data = f.read()
    return data


# ------------------------- 加密方法 --------------------------

def md5_encrypt(data):
    return hashlib.new("md5", data.encode("utf-8")).hexdigest()


def base64_encrypt(data):
    return base64.b64encode(data.encode("utf-8"))


def guid_generate():
    def guid():
        random_number = math.ceil(65536 * (1 + random.random())) | 0
        to_hex_number = format(int(hex(random_number), 16), 'x')
        return to_hex_number[1:]

    return guid() + guid() + "-" + guid() + "-" + guid() + "-" + guid() + "-" + guid() + guid() + guid()


def form_data_generate():
    form_data = json.loads(read_source_data("form.data.json"))
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    day_time = current_time[:10]
    mid = md5_encrypt(guid_generate())
    form_data.update(time=current_time, dt=day_time, mid=mid, source=url)
    return form_data


# 注册验证的签名生成方法
def signature_generate(mid):
    signature_data = {
        "appid": "1014",
        "platid": "4",
        "clientver": "0",
        "clienttime": str(int(time.time())),
        "signature": "",
        "mid": mid,
        "userid": "0",
        "uuid": "73b74ff3d330481db755df420ec3b08d",  # 固定值
        "p.token": ""
    }
    value_array = sorted([v for v in signature_data.values()])
    signature_encrypt = md5_encrypt("1014" + "".join(value_array) + "1014")
    signature_data.update(signature=signature_encrypt)
    return signature_data


# ------------------------- 搜索结果 --------------------------

current_form_data = form_data_generate()
encrypt_form_data = base64_encrypt(json.dumps(current_form_data))
value_mid = current_form_data["mid"]
signature_params = signature_generate(value_mid)

url_register = "https://userservice.kugou.com/risk/v1/r_register_dev"
signature_resp = session.post(url_register, params=signature_params, data=encrypt_form_data)
value_dfid = signature_resp.json()["data"]["dfid"]
timestamp = str(int(time.time()))
value_dfid_collect = md5_encrypt(timestamp)

signature_params_complex_search: list = [
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
    "appid=1014",
    "bitrate=0",
    "callback=callback123",
    f"clienttime={timestamp}",
    "clientver=1000",
    f"dfid={value_dfid}",
    "filter=10",
    "inputtype=0",
    "iscorrection=1",
    "isfuzzy=0",
    f"keyword={keyword}",
    f"mid={value_mid}",
    "page=1",
    "pagesize=30",
    "platform=WebFilter",
    "privilege_filter=0",
    "srcappid=2919",
    "token=",
    "userid=0",
    f"uuid={value_mid}",
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
]

request_params_complex_search: dict = {}
request_params_complex_search.update({k: v for k, v in (i.split("=") for i in signature_params_complex_search[1:-1])})
request_params_complex_search.update(signature=md5_encrypt("".join(signature_params_complex_search)))

headers.update({
    "Accept": "*",
    "Cookie": f"kg_mid={value_mid}; kg_dfid={value_dfid}; kg_dfid_collect={value_dfid_collect}",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-Ch-Ua-Mobile": "?0",
})

session.headers = headers
url_complex_search = "https://complexsearch.kugou.com/v2/search/song"
resp_complex_search = session.get(url_complex_search, params=request_params_complex_search)
text_resp = resp_complex_search.text

result_complex_search = re.search("^callback123\((.*?)\)$", text_resp).group(1)
result_complex_search = json.loads(result_complex_search)

# 数据筛选 —— Name Sings Album Time FileHash EMixSongID
count_total_number = result_complex_search["data"]["total"]
list_complex_search = result_complex_search["data"]["lists"]
infos_complex_search: list = []
for i in list_complex_search:
    temp_dict: dict = {
        "name": i["SongName"],
        "album": i["AlbumName"],
        "id": i["EMixSongID"],
        "singers": i["SingerName"],
        "hash": i["FileHash"]
    }
    time_length = int(i["Duration"]) * 1e3
    change_to_minutes = "%02d:%02d" % (time_length // (60 * 1000), time_length % (60 * 1000) // 1000)
    temp_dict.update({"time": change_to_minutes})
    infos_complex_search.append(temp_dict)


# ------------------------- 详情展示 --------------------------

def display_info(infos):
    max_name_length = 50
    max_singers_length = 50
    max_album_length = 40
    top_line = "| 序号" + " "*6 + "标题" + " "*max_name_length + "歌手" + " "*max_singers_length + "专辑" + " "*max_album_length + "时长 |"
    max_line_length = len(top_line)
    print("-" * (max_line_length + 10))
    print(top_line)

    def print_line(number, info):

        name_, singers_, album_, time_ = info["name"], info["singers"], info["album"], info['time']
        length_name_, length_singers_, length_album_ = len(name_), len(singers_), len(album_)

        name_ = name_ if (length_name_ < max_name_length) else (name_[:max_name_length] + "...")
        singers_ = singers_ if (length_singers_ < max_singers_length) else (singers_[:max_singers_length] + "...")
        album_ = album_ if (length_album_ < max_album_length) else (album_[:max_album_length] + "...")

        temp_string = f"| {number}" +\
                      " " * (7 - len(str(number))) + \
                      name_ + \
                      " " * (max_name_length - length_name_) + \
                      singers_ + \
                      " " * (max_singers_length - length_singers_) + \
                      album_ + \
                      " " * (max_album_length - length_album_)

        print(temp_string + " " * (max_line_length - len(temp_string)) + f"{time_} |")

    for n, i in enumerate(infos, 1):
        print_line(n, i)
    print("-"*(len(top_line)+10))


print(f"Total: {count_total_number}")
display_info(infos_complex_search)

# ------------------------- 单曲选择 --------------------------

select_number = input("Enter Selected Number[1-30]: ").strip()
if select_number and select_number.isdigit():
    select_number = int(select_number)
    if 1 <= select_number <= 30:
        select_number = select_number - 1
else:
    raise ValueError("An Error Number Inputted.")

song_id = infos_complex_search[select_number]["id"]
# ------------------------- 单曲详情 --------------------------

# temp_song_id = infos_complex_search[0]["id"]
url_mix_song = f"https://www.kugou.com/mixsong/{song_id}.html"

timestamp = str(int(time.time()))
random_number = "66" + str(math.floor(99 * random.random() + 1)) + timestamp
ACK_SERVER_10015 = parse.quote("{\"list\":[[\"gzlogin-user.kugou.com\"]]}")
ACK_SERVER_10016 = parse.quote("{\"list\":[[\"gzreg-user.kugou.com\"]]}")
ACK_SERVER_10017 = parse.quote("{\"list\":[[\"gzverifycode.service.kugou.com\"]]}")
params_mixsong = {"fromsearch": keyword}
request_cookie_mixsong = f"kg_mid={value_mid}; " \
                         f"kg_dfid={value_dfid}; " \
                         f"kg_dfid_collect={value_dfid_collect}; " \
                         f"Hm_lvt_aedee6983d4cfc62f509129360d6bb3d={timestamp}; " \
                         f"Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d={timestamp}; " \
                         f"KuGooRandom={random_number}; " \
                         f"kg_mid_temp={value_mid}; " \
                         f"ACK_SERVER_10015={ACK_SERVER_10015}; " \
                         f"ACK_SERVER_10016={ACK_SERVER_10016}; " \
                         f"ACK_SERVER_10017={ACK_SERVER_10017}"

headers.update({
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Cookie": request_cookie_mixsong,
    "Referer": "https://www.kugou.com/yy/html/search.html",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
    "If-Modified-Since": datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT")
})
session.headers = headers
session.get(url_mix_song, params=params_mixsong)

# ------------------------- 单曲获取 --------------------------

url_song_info = "https://wwwapi.kugou.com/play/songinfo"

signature_song_info_params = [
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
    "appid=1014",
    f"clienttime={int(time.time() * 1000)}",
    "clientver=20000",
    f"dfid={value_dfid}",
    f"encode_album_audio_id={song_id}",
    f"mid={value_mid}",
    "platid=4",
    "srcappid=2919",
    "token=",
    "userid=0",
    f"uuid={value_mid}",
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
]
request_params_song_info: dict = {}
request_params_song_info.update({k: v for k, v in (i.split("=") for i in signature_song_info_params[1:-1])})
request_params_song_info.update(signature=md5_encrypt("".join(signature_song_info_params)))

remove_list = ["Upgrade-Insecure-Requests", "Cookie", "If-Modified-Since", "Sec-Fetch-User"]
[headers.pop(key) for key in remove_list]
headers.update({
    "Accept": "*/*",
    "Origin": "https://www.kugou.com",
    "Referer": "https://www.kugou.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
})
session.headers = headers
resp_song_info = session.get(url_song_info, params=request_params_song_info)

# print(resp_song_info.request.url)
# print(resp_song_info.request.headers)
# print(resp_song_info.text)

data_song_info = resp_song_info.json()["data"]
song_info: dict = {}
try:
    song_info.update({
        "timelength": data_song_info["timelength"],
        "filesize": data_song_info["filesize"],
        "song_name": data_song_info["song_name"],
        "author_name": data_song_info["author_name"],
        "lyrics": data_song_info["lyrics"],
        "play_url": data_song_info["play_url"],
        "play_backup_url": data_song_info["play_backup_url"],
        "bitrate": data_song_info["bitrate"],
        "album_name": data_song_info["album_name"],
        "img": data_song_info["img"]
    })
except KeyError as e:
    print("KeyError: ", e)
    print(data_song_info)


# --------------------------- 下载 ----------------------------
def create_directory(name):
    chdir(path.dirname(path.dirname(__file__)))
    if not path.exists(name):
        makedirs(name)
        print("Save Path: ", path.abspath(name))


def save_to_media(link, name, singer):
    directory_name = "Music"
    create_directory(directory_name)

    app_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.1; OPPO R9sk) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/76.0.3809.111 Mobile Safari/537.36"
        }

    with closing(requests.get(link, headers=app_headers, stream=True)) as stream:
        chunk_size = 1024
        content_size = int(stream.headers['content-length'])
        data_count = 0
        with open(f"{directory_name}\\{singer} - {name}.mp3", "wb") as f:
            for data in stream.iter_content(chunk_size=chunk_size):
                f.write(data)
                done_block = int((data_count / content_size) * 50)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r %s:[%s%s] %d%%" % (name, done_block * "█", " " * (50 - 1 - done_block), now_jd), end=" ")


def save_to_text(content, name, singer):
    directory_name = "Music"
    create_directory(directory_name)

    file_name = f"{singer} - {name}.lrc"
    with open(f"{directory_name}\\{file_name}", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nSaved Success: " + file_name)


# 下载歌曲
music_name = song_info["song_name"]
music_singer = song_info["author_name"]
music_play_url = song_info["play_url"]
save_to_media(music_play_url, music_name, music_singer)

# 下载歌词
music_lyrics = song_info["lyrics"]
if music_lyrics:
    save_to_text(music_lyrics, music_name, music_singer)
