import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


class Application(tk.Tk):
    '''
    文件夹选择程序
        界面与逻辑分离
    '''

    def __init__(self):
        '''初始化'''
        super().__init__()  # 有点相当于tk.Tk()

        self.createWidgets()

    def createWidgets(self):
        '''界面'''
        self.title('文件夹选择程序')
        self.columnconfigure(0, minsize=50)

        # 定义一些变量
        self.entryvar = tk.StringVar()
        self.keyvar = tk.StringVar()
        self.keyvar.set('关键字')
        items = ['BufferPool', 'Close', 'Data Capture', 'Compress', 'Pqty', 'Sqty']

        # 先定义顶部和内容两个Frame，用来放置下面的部件
        topframe = tk.Frame(self, height=80)
        contentframe = tk.Frame(self)
        topframe.pack(side=tk.TOP)
        contentframe.pack(side=tk.TOP)

        # 顶部区域（四个部件）
        # -- 前三个直接用 tk 的 widgets，第四个下拉列表 tk 没有，ttk 才有，比较麻烦
        glabel = tk.Label(topframe, text='当前文件夹:')
        gentry = tk.Entry(topframe, textvariable=self.entryvar)
        gbutton = tk.Button(topframe, command=self.__opendir, text='选择')
        gcombobox = ttk.Combobox(topframe, values=items, textvariable=self.keyvar)
        # -- 绑定事件
        gentry.bind('<Return>', func=self.__refresh)
        # gcombobox.bind('<ComboboxSelected>', func=self.__refresh) # 绑定 <ComboboxSelected> 事件
        # -- 放置位置
        glabel.grid(row=0, column=0, sticky=tk.W)
        gentry.grid(row=0, column=1)
        gbutton.grid(row=0, column=2)
        gcombobox.grid(row=0, column=3)

        # 内容区域（三个部件）
        # -- 前两个滚动条一个竖直一个水平
        rightbar = tk.Scrollbar(contentframe, orient=tk.VERTICAL)
        bottombar = tk.Scrollbar(contentframe, orient=tk.HORIZONTAL)
        self.textbox = tk.Text(contentframe, yscrollcommand=rightbar.set, xscrollcommand=bottombar.set)
        # -- 放置位置
        rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.textbox.pack(side=tk.LEFT, fill=tk.BOTH)
        # -- 设置命令
        rightbar.config(command=self.textbox.yview)
        bottombar.config(command=self.textbox.xview)

    def __opendir(self):
        '''打开文件夹的逻辑'''
        self.textbox.delete('1.0', tk.END)  # 先删除所有

        self.dirname = filedialog.askdirectory()  # 打开文件夹对话框
        self.entryvar.set(self.dirname)  # 设置变量entryvar，等同于设置部件Entry

        if not self.dirname:
            messagebox.showwarning('警告', message='未选择文件夹！')  # 弹出消息提示框

        self.dirlist = os.listdir(self.entryvar.get())
        for eachdir in self.dirlist:
            self.textbox.insert(tk.END, eachdir + '\r\n')

        self.textbox.update()

    def __refresh(self, event=None):
        '''更新的逻辑'''
        self.textbox.delete('1.0', tk.END)  # 先删除所有

        self.dirlist = os.listdir(self.entryvar.get())
        for eachdir in self.dirlist:
            self.textbox.insert(tk.END, eachdir + '\r\n')

        self.textbox.update()

    def addmenu(self, Menu):
        '''添加菜单'''
        Menu(self)


class MyMenu():
    '''菜单类'''

    def __init__(self, root):
        '''初始化菜单'''
        self.menubar = tk.Menu(root)  # 创建菜单栏

        # 创建“文件”下拉菜单
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.file_open)
        filemenu.add_command(label="新建", command=self.file_new)
        filemenu.add_command(label="保存", command=self.file_save)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)

        # 创建“编辑”下拉菜单
        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="剪切", command=self.edit_cut)
        editmenu.add_command(label="复制", command=self.edit_copy)
        editmenu.add_command(label="粘贴", command=self.edit_paste)

        # 创建“帮助”下拉菜单
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="关于", command=self.help_about)

        # 将前面三个菜单加到菜单栏
        self.menubar.add_cascade(label="文件", menu=filemenu)
        self.menubar.add_cascade(label="编辑", menu=editmenu)
        self.menubar.add_cascade(label="帮助", menu=helpmenu)

        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)

    def file_open(self):
        messagebox.showinfo('打开', '文件-打开！')  # 消息提示框
        pass

    def file_new(self):
        messagebox.showinfo('新建', '文件-新建！')  # 消息提示框
        pass

    def file_save(self):
        messagebox.showinfo('保存', '文件-保存！')  # 消息提示框
        pass

    def edit_cut(self):
        messagebox.showinfo('剪切', '编辑-剪切！')  # 消息提示框
        pass

    def edit_copy(self):
        messagebox.showinfo('复制', '编辑-复制！')  # 消息提示框
        pass

    def edit_paste(self):
        messagebox.showinfo('粘贴', '编辑-粘贴！')  # 消息提示框
        pass

    def help_about(self):
        messagebox.showinfo('关于', '作者：kinfinger \n verion 1.0 \n 感谢您的使用！ \n kinfinge@gmail.com ')  # 弹出消息提示框


if __name__ == '__main__':
    # 实例化Application
    app = Application()

    # 添加菜单:
    app.addmenu(MyMenu)

    # 主消息循环:
    app.mainloop()