#coding:utf-8
#file:findfat1.py


import tkinter
import tkinter.messagebox

class Windows:
    def __init__(self):
        self.root=tkinter.Tk()
        #创建菜单
        menu=tkinter.Menu(self.root)
        self.root.config(menu=menu)

         #创建“系统”子菜单
        submenu=tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="关于...")
        submenu.add_separator()
        submenu.add_command(label="退出")
        menu.add_cascade(label="系统",menu=submenu)

         #创建“清理”子菜单
        submenu=tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="扫描垃圾文件")
        submenu.add_command(label="删除垃圾文件")
        menu.add_cascade(label="清理",menu=submenu)

         #创建“查找”子菜单
        submenu=tkinter.Menu(menu,tearoff=0)
        submenu.add_command(label="搜索大文件")
        submenu.add_separator()
        submenu.add_command(label="按名称搜索文件")
        menu.add_cascade(label="搜索",menu=submenu)

         #创建标签，用于显示状态信息
        self.progress=tkinter.Label(self.root,anchor=tkinter.W,text='状态',bitmap='hourglass',compound='left')
        self.progress.place(x=10,y=370,width=480,height=15)


         #创建文本框，显示文件列表
        self.flist=tkinter.Text(self.root)
        self.flist.place(x=10,y=10,width=480,height=350)


        #为文本框添加垂直滚动条
        self.vscroll=tkinter.Scrollbar(self.flist)
        self.vscroll.pack(side='right',fill='y')
        self.flist['yscrollcommand']=self.vscroll.set
        self.vscroll['command']=self.flist.yview

    def MainLoop(self):
        self.root.title("Findfat")
        self.root.minsize(500,400)
        self.root.maxsize(500,400)
        self.root.mainloop()

if __name__=="__main__":
    Windows().MainLoop()