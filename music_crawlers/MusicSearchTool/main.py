# -*- encoding=utf-8 -*-

from tkinter import Tk
from SearchGUI import MusicGUI


if __name__ == "__main__":
    init_window = Tk()
    init_window.resizable(0, 0)
    music_window = MusicGUI(init_window)
    music_window.set_init_window()
    music_window.send_log("欢迎使用音乐搜索工具！")
    init_window.mainloop()