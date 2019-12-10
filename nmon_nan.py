#coding:utf-8
#python 3.4
__AUTHOR__ = '王勇'
version = 0.3

import glob, csv
import sys, os
import datetime, time
from tkinter import *

# 设置日志 毫秒保留前三位 14:18:23.978
def log_info():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]).split(' ')[1] + '：[info] '
def log_error():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]).split(' ')[1] + '：[error] '
def log_warning():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]).split(' ')[1] + '：[warning] '

class Nmonpy:
    '''
    【脚本功能描述】：
    1、批量读入nmon文件，支持linux、aix平台下生成的nmon文件
    2、对nmon文件按各性能指标进行逐个分析：主要是CPU利用率、内存利用率、磁盘IO、网络大小，生成一个总的测试汇总结果
    3、同时针对各个nmon文件，还会生成对应的CSV分析结果，根据采样点输出结果值，更好的了解测试过程服务器性能变化情况，方便性能优化
    4、根据情况，测试工程师可自行通过CSV结果绘制折线图
    【使用方法描述】：
    1、把本工具拷贝至nmon结果所在路径下，直接双机nmonpy.exe（已编译可执行文件），可批量生成CSV测试结果
    【功能增强计划】：
    1、增加log日志功能：在工具运行过程中打印运行日志
    2、增加html折线图报表功能：根据对应的nmon文件，生成各自的html折线图报表
    '''

    def __init__(self, parent, **kwargs):
        '''
        初始化数据
        '''

        #self.frame = Frame(root)        #tkinter模块对象与Class类承接
        #self.frame.pack()
        self.frame = parent
        self.frame.config(**kwargs)
        self.frame.attributes('-topmost', 1)
        self.design()

    def design(self):
        '''
        布局text控件、文本、输入控件；text控件中添加滚条
        :return:
        '''
        fm = Frame(self.frame)

        scroll = Scrollbar(fm, orient=VERTICAL)
        self.path_text = Text(fm, font=('宋体', 11),
                              bg='#FFFEEE', fg='green',
                              width=95, height=22,
                              spacing1=8)
        #self.path_text.pack(fill=X, padx=1, pady=10, side=TOP)
        path = Label(self.frame, text='nmon路径：', font=('宋体', 14))
        self.path_entry = Entry(self.frame, show=None, font=('Arial', 12), width=35)

        scroll.config(command=self.path_text.yview)     # 添加一个frame，text与滚动条进行关联
        self.path_text.config(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.path_text.pack(fill=X, padx=1, pady=10, side=TOP)
        fm.pack()

        path.place(x=20, y=540)
        self.path_entry.place(x=150, y=540)

    def dir(self):
        '''
        初始化输入路径、结果文件、结果文件夹
        :return: nmon_dir, result_file, result_dir
        '''
        nmon_dir = self.path_entry.get()
        resultdir = nmon_dir + '\\Result-' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

        # 打开分析结果文件夹，解决工具部署在盘符根目录下不能打开结果文件夹的问题C:\\Result
        if ':\\\\' in resultdir:
            result_dir = resultdir.replace(':\\\\', ':\\')
            result_file = resultdir + '\服务器资源利用率统计表.csv'
        else:
            result_dir = resultdir
            result_file = resultdir + '\服务器资源利用率统计表.csv'

        return nmon_dir, result_file, result_dir


    def update(self):
        '''
        text控件在内容输出后，进行更新、日志滚屏、获取最后光标
        :return:
        '''
        self.frame.update()
        self.path_text.see(END)  # 在text控件中自动滚动显示log内容
        self.path_text.focus_force()  # 获取光标
        #self.path_text.focus()

    def nmonfile(self, fileName):
        '''
        初始化分解nmon文件，主要获取nmon的监控次数和主机名称
        :param :fileName
        :return: nmontext, self.hostname, filenm, self.progname, self.starttime, self.interval
        '''
        self.path_text.insert(END, log_info() + '对 ' + fileName.split('\\')[-1] + ' 进行初始化\n')
        self.update()
        fileText = open(fileName, 'r', encoding='utf8')
        nmontext = fileText.readlines()
        if 'progname' not in str(nmontext) or 'host' not in str(nmontext) or 'interval' not in str(nmontext):
            self.path_text.insert(END, '\n\n' + log_error() + '************* 发现异常文件 ' + fileName.split('\\')[-1] + ' 没有被分析 *************\n')
            self.update()
            self.path_text.insert(END, log_error() + '************* 请记录名称，在分析结束后检查该文件 *************\n')
            self.update()
            self.path_text.insert(END, '\n')
            self.update()
            time.sleep(3)

            self.hostname = 'error'
            self.progname = ''
            self.starttime = ''
            self.interval = ''
        else:
            for line in nmontext:
                if 'AAA,progname' in line:
                    self.progname = line.split(',')[2].split('\n')[0]           #topas_nmon、aix
                if 'AAA,host' in line:
                    self.hostname = line.split(',')[2]
                if 'AAA,time,' in line:
                    self.starttime = line.split(',')[2].split('\n')[0]     #开始监控时间点，linux nmon：10:23.26   aix nmon：10:23:26
                    if '.' in self.starttime:
                        self.starttime = self.starttime.split('.')[0] + ':10'       #对linux nmon时间戳进行格式化，时间戳中.bug
                if 'AAA,interval' in line:
                    self.interval = line.split(',')[2]
        fileText.close()
        filenm = fileName.split('\\')[-1]    #获取要分析的nmon文件名
        return nmontext, self.hostname, filenm, self.progname, self.starttime, self.interval

    def CPU_AVG(self, nmontext, runtime, interval):
        '''
        计算CPU利用率100-idle
        :param : nmontext, runtime, interval
        :return: cpu_avg, cpu_points, TIME, cpu_user, cpu_sys, cpu_wait
        '''
        self.path_text.insert(END, log_info() + '分析CPU资源\n')
        self.update()
        self.cpu_txt = []
        cpu_user = []
        cpu_sys = []
        cpu_wait = []
        cpu_points = []
        cpu_value = 0.0
        cpu_count = 0
        TIME = []
        self.path_text.insert(END, log_info() + '打点采样时间\n')
        self.update()
        starttime = str(runtime)
        # 初始化TIME列，便于手动绘制折线图
        TIME_format = datetime.datetime.strptime(starttime, '%H:%M:%S')     #从nmon原始结果中分析得到nmon开始监控时间点

        for line in nmontext:
            #print(nmontext)
            if ('CPU_ALL,T' in line) and ('PCPU_ALL,T' not in line) and ('SCPU_ALL,T' not in line):  #排除aix nmon中的PCPU_ALL和SCPU_ALL列
                self.cpu_txt.append(line)
        for CPU in self.cpu_txt:
            cpu_num = 100 - float(CPU.split(',')[5])      #100-idle，CPU利用率
            cpu_points.append(format(cpu_num, ".2f"))      #方便后期做曲线图，保留小数点后2位
            cpu_value = cpu_value + cpu_num     #CPU利用率合计，然后平均
            #统计cpu各项list
            cpu_user.append(CPU.split(',')[2])      # CPU user%
            cpu_sys.append(CPU.split(',')[3])      # CPU sys%
            cpu_wait.append(CPU.split(',')[4])      # CPU wait%
            #初始化采样时间
            time_end = (TIME_format + datetime.timedelta(seconds=int(interval))).strftime("%H:%M:%S")       #timedelta()为增加或者减少时间，可以按hours、minutes、seconds来改变时间点
            TIME.append(str(time_end))
            starttime = TIME[-1]  # 获取TIME list最后序列，然后进行时间初始化
            TIME_format = datetime.datetime.strptime(starttime, '%H:%M:%S')

            cpu_count = cpu_count + 1       #根据for循环次数获取实际监控采样次数
        #计算CPU平均利用率
        #print('cpu_count:', cpu_count)
        cpu_avg = cpu_value / cpu_count
        return cpu_avg, cpu_points, TIME, cpu_user, cpu_sys, cpu_wait

    def MEM_Linux_AVG(self, nmontext):
        '''
        计算内存使用率
        按照((mem_total - mem_free) + (swap_total - swap_free)) / (mem_total + swap_total) 公式计算
        :param:nmontext
        :return:mem_avg, mem_points, memtotal, memuse, swaptotal, swapuse, cache, buffer
        '''
        self.path_text.insert(END, log_info() + '分析Linux系统内存资源，按照((mem_total - mem_free) + (swap_total - swap_free)) / (mem_total + swap_total)方法计算内存利用率\n')
        self.update()
        self.mem_txt = []
        memtotal = []
        memuse = []
        swaptotal = []
        swapuse = []
        mem_points = []
        cache = []
        buffer = []
        mem_use = 0.0
        mem_count = 0
        for line in nmontext:
            if 'MEM,T' in line:
                self.mem_txt.append(line)
        #计算内存
        for mem in self.mem_txt:
            # print(float(mem.split(',')[9]))
            mem_total = float(mem.split(',')[2])    # 获取nmon中物理内存总数
            swap_total = float(mem.split(',')[5])   # 获取nmon中swap内存总数
            mem_free = float(mem.split(',')[6])     # 获取nmon中物理内存空闲数
            swap_free = float(mem.split(',')[9])    # 获取nmon中swap内存空闲数
            mem_num = 100 * ((mem_total - mem_free) + (swap_total - swap_free)) / (mem_total + swap_total)    #获取物理总、交换区总内存使用量
            #print('内存单位（%）：' + str(round(mem_num, 2)))      #方便后期做曲线图
            mem_points.append(format(mem_num, ".2f"))      #方便后期做曲线图
            mem_use = mem_use + mem_num
            mem_count = mem_count + 1       #获取实际监控采样次数

            memtotal.append(mem_total)
            muse = mem_total - mem_free          #计算物理内存使用
            memuse.append(format(muse, ".2f"))
            swaptotal.append(swap_total)
            swapuse.append(swap_total - swap_free)
            cache.append(mem.split(',')[11])
            buffer.append(mem.split(',')[14])
        #计算内存平均使用率
        #print('mem_points', str(mem_points))
        mem_avg = mem_use / mem_count
        return mem_avg, mem_points, memtotal, memuse, swaptotal, swapuse, cache, buffer

    def MEM_AIX_AVG(self, nmontext):
        '''
        计算内存使用率
        按照((mem_total - mem_free) + (swap_total - swap_free)) / (mem_total + swap_total) 公式计算
        :param:nmontext
        :return:mem_avg, mem_points, memtotal, memuse, swaptotal, swapuse, cache, buffer
        '''
        self.path_text.insert(END, log_info() + '分析AIX系统内存资源，按照((mem_total - mem_free) + (space_total - space_free)) / (mem_total + space_total)方法计算内存利用率\n')
        self.update()
        self.mem_txt = []
        self.mem_txtc = []
        memtotal = []
        memuse = []
        space_total = []
        space_use = []
        mem_points = []
        FScache = []
        mem_use = 0.0
        mem_count = 0
        for line in nmontext:
            if 'MEM,T' in line:
                self.mem_txt.append(line)
        #计算内存
        for mem in self.mem_txt:
            # print(float(mem.split(',')[9]))
            mem_total = float(mem.split(',')[6])    # 获取nmon中物理内存总数
            swap_total = float(mem.split(',')[7])   # 获取nmon中swap内存总数
            mem_free = float(mem.split(',')[4])     # 获取nmon中物理内存空闲数
            swap_free = float(mem.split(',')[5])    # 获取nmon中swap内存空闲数
            mem_num = 100 * ((mem_total - mem_free) + (swap_total - swap_free)) / (mem_total + swap_total)    #获取物理总、交换区总内存使用量
            #print('内存单位（%）：' + str(round(mem_num, 2)))      #方便后期做曲线图
            mem_points.append(format(mem_num, ".2f"))      #方便后期做曲线图
            mem_use = mem_use + mem_num
            mem_count = mem_count + 1       #获取实际监控采样次数

            memtotal.append(mem_total)
            muse = mem_total - mem_free          #计算物理内存使用
            memuse.append(format(muse, ".2f"))
            space_total.append(swap_total)
            space_use.append(swap_total - swap_free)
        #获取AIX 文件系统Cache内存占用率
        for line in nmontext:
            if 'MEMNEW,T' in line:
                self.mem_txtc.append(line)
            # 计算内存
        for mem in self.mem_txtc:
            FScache.append(float(mem.split(',')[3]))        #FScache文件系统占用百分比

        #计算内存平均使用率
        #print('mem_points', str(mem_points))
        mem_avg = mem_use / mem_count
        return mem_avg, mem_points, memtotal, memuse, space_total, space_use, FScache

    def DISK_AVG(self, nmontext):
        '''
        获取磁盘IO
        :param:nmontext
        :return:disk_avg, disk_points, disk_r_p, disk_w_p
        '''
        self.path_text.insert(END, log_info() + '分析磁盘IO，以及每个采样点的磁盘繁忙度、磁盘读写详细情况\n')
        self.update()
        self.disk_txt = []
        self.disk_busy = []
        self.disk_w = []
        self.disk_r = []
        diskbusy = []
        disk_points = []
        disk_w_p = []
        disk_r_p = []
        disk_value = 0.0
        disk_count = 0
        for line in nmontext:
            if 'DISKXFER,T' in line:
                self.disk_txt.append(line)
            if 'DISKREAD,T0' in line:
                self.disk_r.append(line)
            if 'DISKWRITE,T0' in line:
                self.disk_w.append(line)
            if 'DISKBUSY' in line:
                self.disk_busy.append(line)
        for disk in self.disk_txt:
            #获取io
            if 'DISKXFER,T0' in disk:
                io_list = disk.split(',')[2:]       #获取从第二个序列开始到最后一个序列的数值，然后这些数值相加，就是具体的IO值
                #print(io_list)
                io_num = sum(eval('['+(','.join(io_list))+']'))    #list列表元素转为数字，然后相加
                #print('磁盘IO单位（IO/s）' + io_num)      #方便后期做曲线图
                disk_points.append(format(io_num, ".2f"))       #获取每个采样点的io数据
                disk_value = disk_value + io_num        #io合计，然后求平均值
                disk_count = disk_count + 1       #获取实际监控采样次数
        #获取每个采样点磁盘利用率%(多个磁盘只统计最大磁盘利用率%)
        for disk_b in self.disk_busy:
            if 'DISKBUSY,T' in disk_b:
                diskbusy_end_list = disk_b.split(',')[-1].split('\n')[0]         #把最后一个序列中的\n进行处理
                diskbusy_new = disk_b.split(',')[2:-1]       #取从第二个位置开始至倒数第二个位置的所有序列，形成新的列表，这样就排除了最后一个序列（最后一个带有\n）
                diskbusy_new.append(diskbusy_end_list)       #把最后一个序列加入到新的列表序列中
                #print('diskbusy_new', diskbusy_new)
                disk_int = list(map(eval, diskbusy_new))
                diskbusy.append(max(disk_int))         #获取新序列中最大的序列值，即单个磁盘最大利用率
        # 获取每个采样点disk read数据
        for diskr in self.disk_r:
            if 'DISKREAD,T0' in diskr:
                disk_r = diskr.split(',')[2:]
                disk_r_p.append(sum(eval('[' + (','.join(disk_r)) + ']')))  # 获取从第二个序列开始到最后一个序列的数值，然后这些数值相加
        #获取每个采样点disk write数据
        for diskw in self.disk_w:
            if 'DISKWRITE,T0' in diskw:
                disk_w = diskw.split(',')[2:]
                disk_w_p.append(sum(eval('['+(','.join(disk_w))+']')))      #获取从第二个序列开始到最后一个序列的数值，然后这些数值相加
        #获取磁盘平均IO
        #print('disk_r_p', disk_r_p)
        disk_avg = disk_value / disk_count
        return disk_avg, disk_points, disk_r_p, disk_w_p, diskbusy

    def NET_AVG(self, nmontext):
        '''
        获取网络读写大小
        :param: nmontext
        :return:net_avg, net_points, line_p, netread, netwrite
        '''
        self.path_text.insert(END, log_info() + '分析网络使用大小\n')
        self.update()
        self.net_txt = []
        netread = []
        netwrite = []
        net_points = []
        line_p = []
        net_value = 0.0
        net_count = 0
        for line in nmontext:
            if 'NET,T' in line:
                self.net_txt.append(line)
        for net in self.net_txt:
            if 'NET' in net:
                net_list = net.split(',')[2:]       #获取最后两列的值
                net_num = sum(eval('['+(','.join(net_list))+']'))    #list列表元素转为数字，然后相加
                #print('网络大小KB/s：', str(round(net_num, 2)))      #方便后期做曲线图
                net_points.append(format(net_num, ".2f"))
                net_value = net_value + net_num
                net_count = net_count + 1       #获取实际监控采样次数

                line_p.append('')       #分隔空列，做分割
                nread = float(net.split(',')[2]) + float(net.split(',')[3])
                netread.append(nread)       #计算网络read
                nwrite = float(net.split(',')[4]) + float(net.split(',')[5])
                netwrite.append(nwrite)      #计算网络write
        #计算网络平均大小
        net_avg = net_value / net_count       #KB
        return net_avg, net_points, line_p, netread, netwrite

    def linuxnmon(self, nmontext, hostname, filenm, starttime, interval, result_file, result_dir):
        '''
        汇总CPU、内存、磁盘IO、网络，以及其他详细资源使用情况，并输出分析结果
        :param: nmontext, hostname, filenm, starttime, interval
        :return:
        '''
        #nmon_dir, result_file, result_dir = self.dir()
        self.path_text.insert(END, log_info() + '汇总Linux系统CPU、内存、磁盘IO、网络等主要资源,生成结果文件路径：' + result_file + '\n')
        self.update()
        # 汇总数据
        cpu, cpu_points, time, cpu_user, cpu_sys, cpu_wait = self.CPU_AVG(nmontext, starttime, interval)
        mem, mem_points, memtotal, memuse, swaptotal, swapuse, cache, buffer = self.MEM_Linux_AVG(nmontext)
        disk, disk_points, disk_r_p, disk_w_p, diskbusy = self.DISK_AVG(nmontext)
        net, net_points, line_p, netread, netwrite = self.NET_AVG(nmontext)

        #'%-30s' % str(filenm[0:35]) +
        #print('%-25s' % str(hostname.strip()[0:30]) + '%-12s' % str(format(cpu, ".2f")+ '%') + '%-15s' % str(format(mem, ".2f") + '%') + '%-15s' % str(format(disk, ".2f")) + '%-12s' % str(format(net, ".2f")))
        self.path_text.insert(END, log_info() + '汇总CPU利用率％、 内存利用率％、 磁盘IO、网络使用大小 \n')
        self.update()
        self.path_text.insert(END, log_info() + 'CPU：' + str(format(cpu, ".2f")+ '%') + '  内存：'  +  str(format(mem, ".2f") + '%') + '  磁盘IO：' + str(format(disk, ".2f") + 'IO/s') + '  网络大小：' + str(format(net, ".2f") + 'KB/s') + '\n')
        self.update()
        #生成各个nmon文件的结果汇总表
        with open(result_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([str(filenm), str(hostname.strip()), str(format(cpu, ".2f")), str(format(mem, ".2f")), str(format(disk, ".2f")), str(format(net, ".2f"))])
            csvfile.close()
        filenm_ana = filenm.split('.nmon')[0]       #对分析结果名称进行初始化
        filenm_anacsv = str(filenm_ana) + '.csv'
        self.path_text.insert(END, log_info() + '生成详细资源使用结果：' + result_dir + '\\' + filenm_anacsv + '\n')
        self.update()
        #生成各个nmon文件的监控过程结果，可以手动在cvs结果中生成折线图，filenm_anacsv为文件名称
        with open(result_dir + '\\' + filenm_anacsv, 'w', newline='') as csvfile:
            w_clo = csv.writer(csvfile)
            w_clo.writerow(['采样时间', 'CPU(%)', 'MEM(%)', 'Disk(io/s)', 'Net(KB/s)', '', 'cpu-us%', 'cpu-sys%', 'cpu-wait%', 'diskbusy%', 'diskread KB/s', 'diskwrite KB/s', 'memtotal KB/s', 'memuse KB/s', 'swaptotal KB/s', 'swapuse KB/s', 'cache KB/s', 'buffer KB/s', 'netread KB/s', 'netwrite KB/s'])
            w_clo.writerows(zip(time, cpu_points, mem_points, disk_points, net_points, line_p, cpu_user, cpu_sys, cpu_wait, diskbusy, disk_r_p, disk_w_p, memtotal, memuse, swaptotal, swapuse, cache, buffer, netread, netwrite))  # 使用zip把TIME，CPU, MEM, DISK_IO, NET_KBS等4个list的数据按列存放，根据需要后面可加入其它列，比如cpu-usr、cpu-sys、disk-read、disk-write
            w_clo.writerow('')
            w_clo.writerow(['注意：请性能测试人员根据实际情况是否截头去尾，灵活自主的绘制折线图'])
            csvfile.close()

    def aixnmon(self, nmontext, hostname, filenm, starttime, interval, result_file, result_dir):
        '''
        汇总CPU、内存、磁盘IO、网络，以及其他详细资源使用情况，并输出分析结果
        :param: nmontext, hostname, filenm, starttime, interval
        :return:
        '''
        #nmon_dir, result_file, result_dir = self.dir()
        self.path_text.insert(END, log_info() + '汇总Linux系统CPU、内存、磁盘IO、网络等主要资源,生成结果文件路径：' + result_file + '\n')
        self.update()
        #汇总数据
        cpu, cpu_points, time, cpu_user, cpu_sys, cpu_wait = self.CPU_AVG(nmontext, starttime, interval)
        mem, mem_points, memtotal, memuse, spacetotal, space_use, FSCache = self.MEM_AIX_AVG(nmontext)
        disk, disk_points, disk_r_p, disk_w_p, diskbusy = self.DISK_AVG(nmontext)
        net, net_points, line_p, netread, netwrite = self.NET_AVG(nmontext)

        #print('%-25s' % str(hostname.strip()[0:30]) + '%-12s' % str(format(cpu, ".2f") + '%') + '%-15s' % str(format(mem, ".2f") + '%') + '%-15s' % str(format(disk, ".2f")) + '%-12s' % str(format(net, ".2f")))
        #print()
        self.path_text.insert(END, log_info() + '汇总CPU利用率％、 内存利用率％、 磁盘IO、网络使用大小 \n')
        self.update()
        self.path_text.insert(END, log_info() + 'CPU：' + str(format(cpu, ".2f") + '%') + '  内存：' + str(
            format(mem, ".2f") + '%') + '  磁盘IO：' + str(format(disk, ".2f") + 'IO/s') + '  网络大小：' + str(
            format(net, ".2f") + 'KB/s') + '\n')
        self.update()
        # 生成各个nmon文件的结果汇总表
        with open(result_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([str(filenm), str(hostname.strip()), str(format(cpu, ".2f")), str(format(mem, ".2f")),
                             str(format(disk, ".2f")), str(format(net, ".2f"))])
            csvfile.close()
        filenm_ana = filenm.split('.nmon')[0]  # 对分析结果名称进行初始化
        filenm_anacsv = str(filenm_ana) + '.csv'
        self.path_text.insert(END, log_info() + '生成详细资源使用结果：' + result_dir + '\\' + filenm_anacsv + '\n')
        self.update()
        # 生成各个nmon文件的监控过程结果，可以手动在cvs结果中生成折线图
        with open(result_dir + '\\' + filenm_anacsv, 'w', newline='') as csvfile:
            w_clo = csv.writer(csvfile)
            w_clo.writerow(
                ['采样时间', 'CPU(%)', 'MEM(%)', 'Disk(io/s)', 'Net(KB/s)', '', 'cpu-us%', 'cpu-sys%', 'cpu-wait%',
                 'diskbusy%', 'diskread KB/s', 'diskwrite KB/s', 'mem total KB/s', 'mem use KB/s', 'Space total KB/s',
                 'Space use KB/s', 'FScache(%)', 'netread KB/s', 'netwrite KB/s'])
            w_clo.writerows(
                zip(time, cpu_points, mem_points, disk_points, net_points, line_p, cpu_user, cpu_sys, cpu_wait,
                    diskbusy, disk_r_p, disk_w_p, memtotal, memuse, spacetotal, space_use, FSCache, netread,
                    netwrite))  # 使用zip把TIME，CPU, MEM, DISK_IO, NET_KBS等4个list的数据按列存放，根据需要后面可加入其它列，比如cpu-usr、cpu-sys、disk-read、disk-write
            w_clo.writerow('')
            w_clo.writerow(['注意：请性能测试人员根据实际情况是否截头去尾，灵活自主的绘制折线图'])
            csvfile.close()

    def ps(self, nmonnum, aixnum, result_file, result_dir, error_nmon):
        #nmon_dir, result_file, result_dir = self.dir()
        # 在总结果csv文件中增加说明
        with open(result_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([])
            writer.writerow(['共发现 ' + str(nmonnum) + ' 个nmon文件，' + str(nmonnum - aixnum) + ' 个Linux版本、' + str(aixnum) + ' 个AIX版本' ])
            writer.writerow([])
            if 'nmon' in error_nmon:
                writer.writerow(['异常nmon文件：' + str(error_nmon.split('#|')[:-1]) + '，请自查'])
            else:
                writer.writerow(['本次分析没有发现异常'])
            csvfile.close()
        self.path_text.insert(END, '\n   ================ 您好，nmonpy已完成分析。 分析汇总如下： ==================\n')
        self.update()
        self.path_text.insert(END, '\n' + log_info() + '共发现 ' + str(nmonnum) + ' 个nmon文件，' + str(nmonnum - aixnum) + ' 个Linux版本、' + str(
            aixnum) + ' 个AIX版本\n')
        self.update()

        if 'nmon' in error_nmon:
            self.path_text.insert(END, log_warning() + '异常nmon文件： ' + str(error_nmon.split('#|')[:-1]) + '，请记录\n')
            self.update()
        else:
            self.path_text.insert(END, log_info() + '本次分析没有发现异常')
            self.update()

        self.path_text.insert(END, log_info() + '最终结果：' + result_dir + '\n')
        self.update()
        self.path_text.insert(END, log_info() + 'See You！\n')
        self.update()
        self.path_text.focus()

    def main_nmon(self):
        nmonnum = 0
        aixnum = 0
        error_nmon = ''
        nmon_dir, result_file, result_dir = self.dir()
        try:
            # 判断输入的路径是否存在
            #print(os.path.isdir(nmon_dir))     #False or True，可以采用if判断
            os.listdir(nmon_dir)
        except:
            #使用sys打印最后的异常
            self.path_text.insert(END, log_error() + str(sys.exc_info()[1]) + '\n')
            self.update()
            self.path_text.insert(END, log_info() + '请重新输入存在的路径' + '\n')
            self.update()
            self.path_entry.delete(0, END)  # 清空路径信息
        #else:
        nmons = os.listdir(nmon_dir)

        for k in range(len(nmons)):
            nmons[k] = os.path.splitext(nmons[k])[1]

        # 提取文件夹内所有文件的后缀，如果.nmon格式文件不存在，则直接退出程序
        if '.nmon' not in nmons:
            self.no_nmon()
        else:
            # 判断result目录是否存在，不存在则创建，用于存放分析后结果
            if not os.path.exists(result_dir):
                os.mkdir(result_dir)
            # '%-28s' % '文件名称' +
            #print('%-16s' % '主机名称' + '%-10s' % 'CPU利用率％' + '%-10s' % '内存利用率％' + '%-10s' % '磁盘（IO/s）' + '%-10s' % '网络（KB/s）\n')
            self.path_text.insert(END, log_warning() + '发现目标，请稍等片刻，开始进行分析工作。\n')
            self.update()
            with open(result_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['文件名称', '主机名称', 'CPU利用率（%）', '内存利用率（%）', '磁盘IO（io/s）', '网络大小（KB/s）'])
                csvfile.close()
            # 对本地目录下的nmon文件进行统计，并判断是否为linux版本的nmon，然后挨个执行nmon分析
            for nmonname in glob.glob(nmon_dir + '\*.nmon'):
                nmonnum = nmonnum + 1
                # time.sleep(0.05)
                if nmonnum > 0:
                    self.path_text.insert(END, '\n' + log_warning() + '---------开始分析 ' + nmonname.split('\\')[-1] + ' 文件----------\n')
                    self.update()
                    nmontext, hostname, filenm, progname, starttime, interval = self.nmonfile(nmonname)
                    if 'error' not in hostname:
                        # 判断是否为AIX版本nmon if (progname == 'topas_nmon') or ('aix' in progname)
                        if 'AAA,AIX' in nmontext[7]:
                            #记录aix nmon文件数量
                            aixnum = aixnum + 1
                            self.aixnmon(nmontext, hostname, filenm, starttime, interval, result_file, result_dir)  # 对AIX nmon进行分析
                        else:
                            self.linuxnmon(nmontext, hostname, filenm, starttime, interval, result_file, result_dir)  # 对LINUX nmon进行分析
                    else:
                        #异常的nmon文件
                        error_nmon = error_nmon + filenm +'#|'
            #总结
            self.ps(nmonnum, aixnum, result_file, result_dir, error_nmon)
        print()     #结束

    def result_dir(self):
        '''
        避免盘符根目录下“System Volume Information”安全文件夹拒绝访问导致不能获取修改时间属性的问题
        首先搜索'Result-20'开头的文件夹，然后按照文件夹修改时间进行排序，获取最新时间的'Result-20'开头的文件夹，使打开的结果文件更精准
        :return: file_new
        '''
        res_list = []
        nmon_dir, result_file, result_dir = self.dir()
        try:
            # 判断输入的路径是否存在
            #print(os.path.isdir(nmon_dir))     #False or True，可以采用if判断
            os.listdir(nmon_dir)
        except:
            #使用sys打印最后的异常
            self.path_text.insert(END, log_error() + str(sys.exc_info()[1]) + '\n')
            self.update()
            self.path_text.insert(END, log_info() + '请重新输入存在的路径' + '\n')
            self.update()
            self.path_entry.delete(0, END)  # 清空路径信息

        lists = os.listdir(nmon_dir)
        for k in range(len(lists)):
            lists[k] = os.path.splitext(lists[k])[0]
            #获取'Result-20'开头的文件名称，并且没有后缀的属于文件夹
            if 'Result-20' in lists[k] and os.path.splitext(lists[k])[1] == '':
                res_list.append(lists[k])
        # if len(str(res_list)) == 2:
        if 'Result-20' not in str(res_list):
            self.path_text.insert(END, '\n' + log_error() + '没有找到结果文件夹\n')
            self.update()
            self.path_text.insert(END, log_warning() + '为您打开自定义的路径，请核对该路径下是否存在结果目录\n')
            self.update()
            #return nmon_dir
            os.system('start explorer ' + nmon_dir)
        else:
            #按时间排序
            res_list.sort(key=lambda fn: os.path.getmtime(nmon_dir + "/" + fn))
            file_new = os.path.join(nmon_dir, res_list[-1])
            self.path_text.insert(END, '\n' + log_info() + '打开 ' + file_new + ' 结果文件夹\n')
            self.update()
            #return file_new
            os.system('start explorer ' + file_new)


    def no_nmon(self):
        '''
        判断*.nmon文件是否存在
        :return:
        '''
        nmon_dir, result_file, result_dir = self.dir()
        self.path_text.insert(END, '\n' + log_info() + '输入的路径为：' + nmon_dir + ' \n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + 'nmonpy正在寻找nmon文件，请稍等\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + '  ......\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + '  ......\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + ' “正在努力中”\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + '  ......\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_info() + '  ......\n')
        self.update()
        time.sleep(1)
        self.path_text.insert(END, log_error() + '没有找到nmon文件，请重新输入路径信息......\n')
        self.update()
        time.sleep(0)
        self.path_entry.delete(0, END)      #清空路径信息，还会往下执行下面的代码
        #os._exit(0)

    def main(self):
        #欢迎界面
        self.path_text.insert(END,
                              '''                     ==================================================
                     +                                                +
                     +     欢迎使用（XXX内部版本）- XX测试室            +
                     +                                                +
                     ==================================================
          \n'''
             )
        self.path_text.insert(END, '调式代码用地址：[D:\\pythonwork\\workspace\\NmonPy]\n')

        path_entrybt = Button(self.frame, text='nmon分析', command=self.main_nmon, font=('宋体', 11), fg='green')
        resultbt = Button(self.frame, text='打开结果目录', command=self.result_dir, font=('宋体', 11), fg='green')
        #killbt = Button(root, text='中止分析', command=self.kill1, font=('宋体', 11), fg='green')

        path_entrybt.place(x=490, y=538)
        resultbt.place(x=580, y=538)
        #killbt.place(x=700, y=504)

        #self.path_entry.bind('<Enter>', self.main_nmon)        #按回车键代替path_entrybt按钮
        #self.frame.mainloop()

'''
if __name__ == '__main__':

    root = Tk()
    root.title('Nmonpy 欢迎使用HXB内部版本（技术测试室）')
    root.geometry('800x600+400+0')   #宽*高+左边界长度+上边界长度
    root.resizable(False, False)
    root.iconbitmap('test.ico')

    Nmonpy(root).main()
    root.mainloop()
'''