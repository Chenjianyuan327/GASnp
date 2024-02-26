import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
import threading
import inspect
import ctypes
import time
from genetic import genetic
from logo import img
import base64


def stop_thread(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class GUI():
    def __init__(self):
        # 创建主窗口
        init_window = self.createWindow("SNPOptimizer V1")
        # 创建组件
        self.createLabel(init_window)  # 标签
        self.createEntry(init_window)  # 输入框
        self.createCombobox(init_window)  # 下拉列表
        self.createButton()  # 按钮
        self.createText(init_window)  # 文本
        self.createScroll()  # 滑动条
        # 生成界面
        self.start = False
        init_window.mainloop()
        if self.start:
            stop_thread(self.t.ident, SystemExit)

    def thread_it(self, func):
        if self.start:
            stop_thread(self.t.ident, SystemExit)

        '''将函数打包进线程'''
        self.t = threading.Thread(target=func)  # 创建
        self.t.setDaemon(True)  # 守护 !!!
        self.t.start()  # 启动
        self.start = True

    def createWindow(self, name):
        init_window = Tk()  # 实例化出一个父窗口
        init_window.title(name)

        # 打上图标
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))
        tmp.close()
        init_window.iconbitmap("tmp.ico")
        os.remove("tmp.ico")

        # 设置窗口大小
        init_window.geometry('650x360+800+300')  # 290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        # init_window["bg"] = "black"
        return init_window

    def createLabel(self, init_window):
        vcf_label = Label(init_window, text="VCF文件: ")
        vcf_label.grid(row=0, column=0, sticky="w")

        pop_num_label = Label(init_window, text="种群数量: ")
        pop_num_label.grid(row=1, column=0, sticky="w")

        epoch_label = Label(init_window, text="迭代次数: ")
        epoch_label.place(x=120, y=37, width=60, height=25)

        snpL_label = Label(init_window, text="snp长度: ")
        snpL_label.place(x=245, y=37, width=60, height=25)

        mu_label = Label(init_window, text="变异概率: ")
        mu_label.place(x=370, y=37, width=60, height=25)

    def createEntry(self, init_window):
        self.csv_Entry = Entry(init_window, width=70)
        self.csv_Entry.grid(row=0, column=1, sticky="w")

    def createCombobox(self, init_window):
        self.pop_num_Combobox = ttk.Combobox(init_window)
        self.pop_num_Combobox.place(x=61, y=37, width=50, height=25)
        self.pop_num_Combobox["value"] = list(range(10, 102, 2))  # #给下拉菜单设定值
        self.pop_num_Combobox.configure(state='readonly')
        self.pop_num_Combobox.current(10)

        self.epoch_Combobox = ttk.Combobox(init_window)
        self.epoch_Combobox.place(x=180, y=37, width=55, height=25)
        self.epoch_Combobox["value"] = list(range(10, 3010, 10))  # #给下拉菜单设定值
        self.epoch_Combobox.configure(state='readonly')
        self.epoch_Combobox.current(99)

        self.snpL_Combobox = ttk.Combobox(init_window)
        self.snpL_Combobox.place(x=305, y=37, width=55, height=25)
        self.snpL_Combobox["value"] = list(range(1, 1501))  # #给下拉菜单设定值
        self.snpL_Combobox.configure(state='readonly')
        self.snpL_Combobox.current(19)

        self.mu_Combobox = ttk.Combobox(init_window)
        self.mu_Combobox.place(x=430, y=37, width=55, height=25)
        self.mu_Combobox["value"] = (0.1, 0.2, 0.3, 0.4)  # #给下拉菜单设定值
        self.mu_Combobox.configure(state='readonly')
        self.mu_Combobox.current(1)

    def createButton(self):
        dir_Button = Button(text="路径查找", width=10, command=self.dir_callback, overrelief='solid')
        dir_Button.grid(row=0, column=2, padx=2, pady=2, sticky="w")

        gener_Button = Button(text="生成", width=10, command=lambda: self.thread_it(self.gener_callback),
                              overrelief='solid', bg='skyblue')
        gener_Button.grid(row=1, column=2, padx=2, pady=2, sticky="w")

    def createText(self, init_window):
        self.log_Text = Text(init_window, width=70, height=20)
        self.log_Text.grid(row=2, column=1, sticky='w')
        self.log_Text.configure(state='disabled')  # 只读模式

    def createScroll(self):
        log_scroll = Scrollbar(orient="vertical", command=self.log_Text.yview)
        self.log_Text.config(yscrollcommand=log_scroll.set)  # 滑动条填充
        log_scroll.grid(row=2, column=2, sticky=N + S + W)  # 与text关联

    def dir_callback(self):
        path = askopenfilename(title='读入*.vcf文件', filetypes=[('VCF Files', '*.vcf')])
        if len(path):
            self.csv_Entry.delete(0, 'end')
            self.csv_Entry.insert('insert', path)

    def get_set(self):
        path = self.csv_Entry.get()  # 获取路径
        pop_num = int(self.pop_num_Combobox.get())  # 初始种群数量
        epoch = int(self.epoch_Combobox.get())  # 迭代次数
        snpL = int(self.snpL_Combobox.get())  # snp的长度
        mu = float(self.mu_Combobox.get())  # 变异概率
        return path, pop_num, epoch, snpL, mu

    def gener_callback(self):
        path, pop_num, epoch, snpL, mu = self.get_set()

        self.log_Text.configure(state='normal')
        self.log_Text.tag_config("tag_1", foreground="red")
        self.log_Text.tag_config("tag_2", foreground="green")
        if os.path.exists(path):
            try:
                self.log_Text.insert('end', '\n' + '正在优化...请勿关闭软件！！！', "tag_2")
                name, fit = genetic(path, pop_num, epoch, snpL, mu)
                current = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                self.log_Text.insert('end', '\n' + current)
                self.log_Text.insert('end', '\n文件: {} \nSNP长度:{}    能识别:{}个个体\n'.format(path.split('/')[-1], snpL, fit))
                self.log_Text.insert('end', '已生成：')
                self.log_Text.insert('end', name + '\n')
                self.start = False  # 线程已经关闭
            except Exception as error:
                self.log_Text.tag_config("tag_1", foreground="red")
                self.log_Text.insert('end', '\n[*]不正常的vcf文件, 请核对vcf文件内容...' + '\n', "tag_1")
                self.log_Text.insert('end', '\n{}'.format(error) + '\n', "tag_1")
                self.start = False  # 线程已经关闭
        else:
            self.log_Text.insert('end', '\n[*]找不到该文件，请输入正确的vcf文件路径...' + '\n', "tag_1")
            self.start = False  # 线程已经关闭

        self.log_Text.configure(state='disabled')
        self.log_Text.see(END)
        self.start = False  # 线程已经关闭


if __name__ == '__main__':
    GUI()
