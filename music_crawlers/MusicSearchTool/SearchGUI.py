# -*- encoding=utf-8 -*-

import json
import requests
import time
from contextlib import closing
import os
import tkinter
from tkinter import *
from tkinter import messagebox
from KuwoMusic import KWMusic

FILE_NAME = "Music"


class MusicGUI:
    kw_search = KWMusic()

    # 初始化界面
    def __init__(self, init_window_attribute):
        self.init_window = init_window_attribute

        self.width = 1200
        self.height = 720
        self.page = 1
        self.row = 0
        self.font_size = 12
        self.logs = []
        self.spacing = 5
        self.line_list = []
        self.check_button_list = []
        self.turning_page_event_count = 0
        self.download_task = []
        self.music_data = []

    # 设置窗口默认属性
    def set_init_window(self):
        # 设置主窗口名称
        self.init_window.title("音乐搜索工具_v1.0.2")
        # 1200 720表示窗口大小，+350+200定义窗口弹出时的默认展示位置（+x+y），默认打开时居中展示
        screenwidth = self.init_window.winfo_screenwidth()
        screenheight = self.init_window.winfo_screenheight()
        self.init_window.geometry(
            f"{self.width}x{self.height}+{int((screenwidth - self.width) / 2)}+{int((screenheight - self.height) / 2)}")
        # 设置主窗口展示样式
        self.canvas_left = Canvas(self.init_window, width=self.width * 0.6, height=self.height - self.height * 0.17,
                                  bg="white", borderwidth=3, relief="ridge")
        # 画布放置相对位置
        self.canvas_left.place(x=3, y=self.height * 0.1)

        self.canvas_right = Canvas(self.init_window, width=self.width * 0.3 - 12,
                                   height=self.height - self.height * 0.1,
                                   bg="white", borderwidth=3, relief="ridge")
        self.canvas_right.place(x=self.width * 0.7, y=self.height * 0.1 - 10)

        # 输入框位置和样式
        self.text_enter = Entry(self.init_window, width=80, borderwidth=3, relief="ridge",
                                selectforeground="red", selectbackground="white")
        self.text_enter.place(x=6, y=self.height * 0.03)

        # 互动按键位置及样式
        # 搜索
        self.button_search = Button(self.init_window, text="搜索", width=12, command=self.__search)
        self.button_search.place(x=self.width * 0.5, y=self.height * 0.03)

        # 翻页
        self.button_previous_page = Button(self.init_window, text="<< 上一页", width=12, command=self.__previous_page)
        self.button_previous_page.place(x=self.width * 0.6 / 2 - 150, y=self.height * 0.95)
        self.button_next_page = Button(self.init_window, text="下一页 >>", width=12, command=self.__next_page)
        self.button_next_page.place(x=self.width * 0.6 / 2 + 50, y=self.height * 0.95)

        # 显示当前页数本文
        self.text_page_display = Text(self.init_window, width=6, height=1)
        self.text_page_display.insert("insert", f"第{int(self.page)}页")
        self.text_page_display.place(x=self.width * 0.6 / 2 - 25, y=self.height * 0.9 + 45)

        # 下载
        self.button_download = Button(self.init_window, text="下载", width=12, command=self.__download)
        self.button_download.place(x=self.width * 0.6 + 18, y=self.height * 0.2)
        # 全选
        self.button_check_all = Button(self.init_window, text="全选", width=12, command=self.__check_all)
        self.button_check_all.place(x=self.width * 0.6 + 18, y=self.height * 0.3)
        # 退出
        self.button_quit = Button(self.init_window, text="退出", width=12, command=self.__quit)
        self.button_quit.place(x=self.width * 0.6 + 18, y=self.height * 0.8)
        # 清空
        self.clear_all = Button(self.init_window, text="清空", width=12, command=self.__clear_all)
        self.clear_all.place(x=self.width * 0.6 + 18, y=self.height * 0.4)

    # 在搜索内容画布上展示标题栏
    def display_list_line(self):
        self.canvas_left.create_text((self.spacing + 20, 20), text="序号", font=("Arial", self.font_size, "bold"))
        self.canvas_left.create_text((self.spacing + 200, 20), text="标题", font=("Arial", self.font_size, "bold"))
        self.canvas_left.create_text((self.spacing + 400, 20), text="歌手", font=("Arial", self.font_size, "bold"))
        self.canvas_left.create_text((self.spacing + 580, 20), text="专辑", font=("Arial", self.font_size, "bold"))
        self.canvas_left.create_text((self.spacing + 670, 20), text="时长", font=("Arial", self.font_size, "bold"))

    # 复选框控件
    def display_check_button(self, x, y, text):
        var = tkinter.IntVar()
        check_button = Checkbutton(self.canvas_left, text=text, variable=var, borderwidth=1, relief="ridge",
                                   onvalue=True, offvalue=False)
        check_button.place(x=x, y=y)
        return var, check_button

    def display_list_result(self, result: list):
        y = 35
        self.display_list_line()
        max_length_name = 46
        max_length_artist = 30
        max_length_album = 15
        if self.page == 0: self.page = 1
        if self.turning_page_event_count == 0: self.turning_page_event_count = 1
        for num, info in enumerate(result, 1):
            # 字符串截断处理，避免展示过长文本重叠
            name = info['name'][0:max_length_name] + "..." if len(info['name']) > max_length_name else info['name']
            artist = info['artist'][0:max_length_artist] + "..." if len(info['artist']) > max_length_artist else info['artist']
            album = info['album'][0:max_length_album] + "..." if len(info['album']) > max_length_album else info['album']
            obj_check = self.display_check_button(self.spacing + 5, y, num + 20 * (self.page - 1))
            self.check_button_list.append(obj_check)
            self.canvas_left.create_text((self.spacing + 80, y + 12), text=f"{name}",
                                         font=("Arial", self.font_size - 3), anchor="w", tag="line_list")
            self.canvas_left.create_text((self.spacing + 350, y + 12), text=f"{artist}",
                                         font=("Arial", self.font_size - 3), anchor="w", tag="line_list")
            self.canvas_left.create_text((self.spacing + 550, y + 12), text=f"{album}",
                                         font=("Arial", self.font_size - 3), anchor="w", tag="line_list")
            self.canvas_left.create_text((self.spacing + 650, y + 12), text=f"{info['time']}",
                                         font=("Arial", self.font_size - 3), anchor="w", tag="line_list")
            y += 28
        self.text_page_display.delete(1.0, 3.0)
        self.text_page_display.insert("insert", f"第{int(self.page)}页")

    # 文本格式校验
    def check_content(self):
        content = self.text_enter.get().strip().replace("\n", "")
        if content == "":
            self.send_log("ERROR: 输入内容不合法")
        else:
            self.send_log("INFO: 搜索中...")
            self.display_list_line()
            return content.encode()

    # 清空当前展示内容
    def __clear(self):
        self.canvas_left.delete("line_list")
        for i in self.check_button_list: i[1].destroy()  # pack_forget
        self.canvas_left.update()

    # 搜索
    def __search(self):
        self.__clear()
        self.page = 0
        self.line_list.clear()
        self.check_button_list.clear()
        if self.refresh():
            self.send_log(f"INFO: 搜索成功，搜索结果共{self.kw_search.total}条")

    def refresh(self):
        keyword = self.check_content()
        if keyword:
            content = self.kw_search.kw_search(keyword, self.page - 1)
            if content:
                self.music_content = self.format_data(content)
                self.display_list_result(self.music_content)
                self.music_data = self.music_content
                return True

    # 前一页
    def __previous_page(self):
        if self.page > 1:
            self.__clear()
            self.page -= 1
            if self.refresh():
                self.turning_page_event_count += 1

    # 下一页
    def __next_page(self):
        if self.page >= 1 and self.turning_page_event_count >= 1:
            self.__clear()
            self.page += 1
            if self.refresh():
                self.turning_page_event_count += 1

    # 全选
    def __check_all(self):
        state = []
        a = (self.turning_page_event_count - 1) * 20
        b = (self.turning_page_event_count - 1) * 20 + 20
        self.current_check_list = self.check_button_list[a:b]
        [state.append(i[0].get()) for i in self.current_check_list]
        if all(state):
            [v[1].deselect() for v in self.current_check_list]
            return
        for i, v in self.current_check_list:
            if not i.get(): v.select()

    # result是当前页面展示内容
    def __download(self):
        if self.turning_page_event_count >= 1:
            result = self.music_content
            a = (self.turning_page_event_count - 1) * 20
            b = (self.turning_page_event_count - 1) * 20 + 20
            self.current_check_list = self.check_button_list[a:b]
            check_list = [i[0].get() for i in self.current_check_list]
            n = 1
            for i, v in zip(result, check_list):
                if v: self.download_task.append((n, i["seed"]))  # [(1,"267075991"), (3,"267075991")]
                n += 1
            self.task_count = len(self.download_task)
            if self.task_count == 0:
                self.send_log("WARNING: 当前无下载任务")
                return
            # 确认当前页面勾选内容
            self.send_log(f"INFO: 开始下载，当前任务{self.task_count}条")
            # 取消勾选
            [v[1].deselect() for v in self.current_check_list]
            # 执行下载
            self.__downloader(self.download_task, (self.page-1)*20)
            # 清除任务
            self.download_task.clear()

    def __downloader(self, tasks, page_start):
        for i in tasks:
            k, v = i
            self.task_count -= 1
            serial_number = k + page_start
            self.send_log(f"获取序号<{serial_number}>播放地址...")
            try:
                self.play_data = self.kw_search.kw_get_play_url(v)
                url = self.play_data["data"]["url"]
            except (KeyError, json.JSONDecodeError):
                self.send_log(f"获取序号<{serial_number}>播放地址失败，当前剩余任务{self.task_count}条")
                self.send_log(f"请求失败: {self.play_data}")
                continue
            if not os.path.exists(FILE_NAME):
                os.makedirs(FILE_NAME)
                self.send_log(f"INFO: 文件保存目录: {os.path.abspath(FILE_NAME)}")
            title = self.music_data[int(k - 1)]["name"]
            singer = self.music_data[int(k - 1)]["artist"]
            with closing(requests.get(url, headers=self.kw_search.request_header_APP_UA, stream=True)) as resp:
                content_size = int(resp.headers['content-length'])
                size = '%.1f' % (int(content_size) / 1024 / 1024)
                self.send_log(f"序号<{serial_number}>开始下载，大小{size}MB")
                with open(fr"{FILE_NAME}\{singer} - {title}.mp3", "wb") as fp:
                    for data in resp.iter_content(chunk_size=1024):
                        fp.write(data)
                self.send_log(f"序号<{serial_number}>下载成功，当前剩余任务{self.task_count}条")
            time.sleep(1)

    # 重置全部内容
    def __clear_all(self):
        for i in self.check_button_list: i[1].destroy()
        self.__init__(self.init_window)
        self.canvas_left.delete("all")
        self.canvas_left.update()
        self.canvas_right.delete("all")
        self.canvas_right.update()
        self.text_enter.delete(0, "end")
        self.text_page_display.insert("insert", "第1页")

    # 输出日志
    def send_log(self, message):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime(time.time()))
        log_msg = f"{current_time} {message}"
        fill_color = "red" if any(i in message for i in ["ERROR", "WARNING", "FAIL"]) else "black"
        # 文本框单行展示长度
        width_newline = self.width * 0.28
        self.newline_rows = round(len(log_msg) * 16 / width_newline)
        # 默认最大展示行数
        max_text_row = 44
        # 默认行距
        width_row = 20
        width_row = 14 if self.newline_rows > 1 else width_row

        if self.row <= max_text_row:
            obj_log = self.canvas_right.create_text((6, width_row * (self.row + self.newline_rows)),
                                                    fill=fill_color, text=log_msg, width=width_newline, justify="left",
                                                    anchor="w")
        else:
            # 删除首行并更新画布
            self.row = 0
            self.canvas_right.delete(*self.logs)
            self.canvas_right.update()

            obj_log = self.canvas_right.create_text((6, width_row * (self.row + self.newline_rows)),
                                                    fill=fill_color, text=log_msg, width=width_newline, justify="left",
                                                    anchor="w")
        self.row += self.newline_rows
        self.logs.append(obj_log)

    def __quit(self):
        msg = messagebox.askokcancel("退出", "确认是否退出?")
        if msg:
            self.init_window.quit()

    def format_data(self, data: list):
        format_list = []
        for k in data:
            k.setdefault("time", "00:00")
            try:
                play_time = self.kw_search.kw_get_music_info(k["seed"])[0]
                k.update(time=play_time)
            except:
                continue
            format_list.append(k)
        return format_list


# if __name__ == "__main__":
#     init_window = Tk()
#     music_window = MusicGUI(init_window)
#     music_window.set_init_window()
#     init_window.mainloop()
