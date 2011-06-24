#!/usr/bin/env python
# coding=utf-8
#__author__="hechao"
#__date__ ="$2011-6-7 13:29:19$"
import gtk
import gettext
import pango
import os
import misc
import globals
import logging
import locale
import dbus
from threading import Thread

gettext.install('yinst', localedir='/usr/share/locale', unicode=True)

class yinst():

    def __init__(self, parent=None):
        gtk.gdk.threads_init()
        
        #主界面
        self.window = gtk.Window()
        self.window.set_border_width(12)
        self.window.set_size_request(320,180)
        #gtk.window_set_default_icon_name('yinst.ico')
        #设置窗口图标
        gtk.window_set_default_icon_from_file('yinst.ico')
        # set window center
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        # set window title
        self.window.set_title(_("Ylmf OS install programs"))
        self.window.connect('destroy',gtk.main_quit)

        self.main_vbox = gtk.VBox(False,5)
        self.window.add(self.main_vbox)

        self.label_des = gtk.Label("")
        self.label_des.set_markup('<big><b>' + _("To try or install linux from a linux.") + '</b></big>')
        self.main_vbox.pack_start(self.label_des, False, False)

        self.iso_vbox = gtk.VBox(False,2)
        self.main_vbox.pack_start(self.iso_vbox, False, False)

        self.label_iso = gtk.Label("")
        self.label_iso.set_markup(_("iso file :"))
        self.hbox_label = gtk.HBox(False,5)
        self.hbox_label.pack_start(self.label_iso, False, False)
        self.iso_vbox.pack_start(self.hbox_label,False,False)

        self.scroll_win = gtk.ScrolledWindow()
        self.scroll_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll_win.set_shadow_type (gtk.SHADOW_IN)
        #self.scroll_win.set_size_request(300,100)

        list_store = gtk.ListStore(str)
	self.treeview = gtk.TreeView(list_store)
	self.__add_columns(self.treeview)
	self.scroll_win.add(self.treeview)
        self.iso_vbox.pack_start(self.scroll_win,False,False)

        self.open_button = gtk.Button(stock=gtk.STOCK_ADD)
        self.open_button.connect("clicked",self.add_iso)

        self.hbox_button = gtk.HBox(False,5)
        self.hbox_button.pack_end(self.open_button,False,False)

        self.install_button = gtk.Button(_("install"))
        self.install_button.connect("clicked",self.install)
        self.install_button.set_sensitive(False)

        self.hbox_button.pack_start(self.install_button,False,False)
        self.iso_vbox.pack_start(self.hbox_button)

        #安装界面
        self.install_window = gtk.Window()
        self.install_window.set_border_width(12)
        self.install_window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        #设置窗口标题
        self.install_window.set_title(_("Installing"))
        self.install_window.connect_object('destroy',gtk.Widget.destroy,self.window)

        #不可调整窗口大小
        self.install_window.set_resizable(False)

        #设置为模态窗口（类似于对话框）
        self.install_window.set_modal(True)

        #不显示关闭按钮
        self.install_window.set_deletable(False)

        #进度条box
        self.progress_vbox = gtk.VBox(False,5)

        #进度条上的文字（粗体）
        self.progress_title = gtk.Label("")
        self.progress_vbox.pack_start(self.progress_title,False,False)

        #进度条
        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_size_request(400,-1)
        self.progressbar.set_pulse_step(0.1)
        self.progress_vbox.pack_start(self.progressbar,False,False)

        #进度条下的描述信息
        self.progress_hbox = gtk.HBox(False,5)
        self.progress_info = gtk.Label("")
        self.progress_hbox.pack_start(self.progress_info,False,False)

        #取消按钮
        self.progress_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.progress_cancel.connect("clicked",self.install_exit)
        self.progress_hbox.pack_end(self.progress_cancel,False,False)

        #重启按钮
        self.progress_reboot = gtk.Button(_("Reboot"))
        self.progress_reboot.connect("clicked",self.reboot)
        self.progress_hbox.pack_end(self.progress_reboot,False,False)

        self.progress_vbox.pack_start(self.progress_hbox,False,False)

        self.install_window.add(self.progress_vbox)
        
        #设置日志文件
        misc.set_logger()

        self.sources = {}
        self.names = {}
        self.icons = {}

        self.window.show_all()

        gtk.main()

    def add_iso(self, *args):
        filename = ''
        chooser = gtk.FileChooserDialog(_("choose a iso file"), #打开窗口的标题
                                        None,                   #父窗口
                                        gtk.FILE_CHOOSER_ACTION_OPEN, #窗口标志
                                        (gtk.STOCK_CANCEL,      #添加取消按钮
                                        gtk.RESPONSE_CANCEL,    #取消按钮返回值
                                        gtk.STOCK_OPEN,         #添加打开按钮
                                        gtk.RESPONSE_OK)        #打开按钮返回值
                                        )
        filter = gtk.FileFilter()
        filter.add_pattern("*.iso")         #限定文件后缀
        filter.set_name(_('ISO Images'))    #设置filter类型名
        chooser.add_filter(filter)          #添加filter到dialog框中
        folder = os.path.expanduser('~')
        chooser.set_current_folder(folder)  #设置默认目录
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
            self.add_info(filename)
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()
        chooser.destroy()

    def add_info(self,filename):
        #获取iso的绝对路径，如果有"~"，则用用户路径来替换
        filename = os.path.abspath(os.path.expanduser(filename))
        logging.debug("iso path %s" %filename)

        if not os.path.isfile(filename):
            return
        if filename in self.sources:
            return

        #分离文件名[0]和扩展名[1]
        extension = os.path.splitext(filename)[1]

        if not extension:
            return

        extension = extension.lower()
        if extension == '.iso':
            label = self._is_casper_cd(filename)
            if label:
                self.sources[filename] = {
                    'device' : filename,
                    'size' : os.path.getsize(filename),
                    'label' : label.rstrip('\n'),
                    'type' : globals.SOURCE_ISO,
                }
                logging.debug(self.sources[filename])
                model = self.treeview.get_model()
                new_iter = model.append([filename])
                
                if self.treeview.get_selection().get_selected()[1] is None:
                    self.treeview.set_cursor(model.get_path(new_iter))
                #激活安装按钮
                self.install_button.set_sensitive(True)

    def _is_casper_cd(self, filename):
        cmd = ['isoinfo', '-J', '-i', filename, '-x', '/.disk/info']
        try:
            output = misc.popen(cmd, stderr=None)
            if output:
                return output
        except:
            logging.error('Could not extract .disk/info.')
            return None

    def __add_columns(self, treeview):

        cell_name = gtk.CellRendererText()
        cell_name.set_property('ellipsize', pango.ELLIPSIZE_END)
        cell_pixbuf = gtk.CellRendererPixbuf()
        column_name = gtk.TreeViewColumn(_('Image'))
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column_name.set_resizable(True)
        column_name.set_expand(True)
        column_name.set_min_width(75)
        column_name.pack_start(cell_pixbuf, expand=False)
        column_name.pack_start(cell_name, expand=True)
        self.treeview.append_column(column_name)
        column_name.set_cell_data_func(cell_name, self.column_data_func, 0)
        column_name.set_cell_data_func(cell_pixbuf, self.pixbuf_data_func)

        cell_version = gtk.CellRendererText()
        cell_version.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_name = gtk.TreeViewColumn(_('OS Version'), cell_version)
        column_name.set_cell_data_func(cell_version, self.column_data_func, 1)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column_name.set_resizable(True)
        column_name.set_expand(True)
        column_name.set_min_width(75)
        self.treeview.append_column(column_name)

        cell_size = gtk.CellRendererText()
        cell_size.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_name = gtk.TreeViewColumn(_('Size'), cell_size)
        column_name.set_cell_data_func(cell_size, self.column_data_func, 2)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column_name.set_resizable(True)
        column_name.set_expand(False)
        column_name.set_min_width(75)
        self.treeview.append_column(column_name)

    def column_data_func(self, layout, cell, model, iterator, column):
        udi = model[iterator][0]
        dev = self.sources[udi]
        if column == 0:
            cell.set_property('text', dev['device'])
        elif column == 1:
            cell.set_property('text', dev['label'])
        elif column == 2:
            cell.set_property('text', misc.format_size(dev['size']))

    def pixbuf_data_func(self, column, cell, model, iterator):
        udi = model[iterator][0]
        dev = self.sources[udi]
        source_type = dev['type']
        if source_type == globals.SOURCE_ISO:
            cell.set_property('stock-id', gtk.STOCK_CDROM)

    def install(self,*args):

        logging.debug("install...")
        self.window.hide()
        self.install_window.show_all()
        self.progress_reboot.hide()

        isopath = self.get_iso()
        targetpath = globals.configdir + "/" +"livecd.iso"
        logging.debug('Starting install thread.')
        self.install_thread = progress(isopath,targetpath)
        self.install_thread.progress = self.progress
        self.install_thread.start()

    def install_exit(self,*args):
        logging.debug("exit install")
        self.install_window.destroy()
        self.window.destroy()

    def reboot(self,*args):
        logging.debug("reboot computer")
        #用dbus调用系统reboot
        bus = dbus.SessionBus()
        devobj = bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
	power = dbus.Interface(devobj, "org.gnome.SessionManager")
        power.RequestReboot()

    def progress_message(self, message):
        self.progress_title.set_markup('<big><b>' + message + '</b></big>')

    def progress(self, source, target):

        logging.debug("start progress")
        #复制文件到$HOME/.yinst下
        self.progress_message(_('Copying files...'))

        if os.path.isfile(source):
            file_size = os.path.getsize(source) / (1024**2)*1.0

        source_file = open(source, "rb")
        target_file = open(target, "wb")
        logging.debug('Writing %s' % target)
        data_read = 0
        while True:
            data = source_file.read(1024**2)
            data_read += 1
            if data == "":
                break
            target_file.write(data)
            complete = data_read / file_size
            if complete >= 0.98:
                complete = 0.98
            self.progressbar.set_fraction(complete)
            self.progress_info.set_markup(_("Complete:") + " %.2f" % (float(complete) * 100) + "%" )
            if data_read >= file_size:
                break
        source_file.close()
        target_file.close()

        #设置grub启动项
        self.grub_config(target)

        self.progress_message(_('Installation complete'))
        self.progressbar.set_fraction(1)
        self.progress_cancel.hide()
        self.progress_reboot.show()
        logging.debug("Installation complete")

    def grub_config(self, target):

        logging.debug("setup grub")
        target = target.replace("/home","")
        self.progress_message(_('Setup grub...'))
        language, encoding = locale.getdefaultlocale()
        zh_cn = "%s.%s" %(language, encoding)
        filename = "/etc/grub.d/05_livecd"

        try:
            logging.debug("callable dbus")
            bus = dbus.SystemBus()
            obj = bus.get_object('com.ylmf.yinst','/com/ylmf/yinst')
            face = dbus.Interface(obj, 'com.ylmf.yinst')
            face.write_file(target, zh_cn, filename)
        except dbus.DBusException:
            logging.error("dbus error")

        self.progress_info.set_markup(_("The installation is complete.  You may now reboot your computer"))

    def get_iso(self):

        sel = self.treeview.get_selection()
        m, i = sel.get_selected()
        if i:
            return m[i][0]
        else:
            logging.debug('No source selected.')
            return ''

class progress(Thread):
    def __init__(self, isopath,targetpath):
        Thread.__init__(self)
        self.setDaemon(True)

        self.isopath = isopath
        self.targetpath = targetpath

    def progress(self, isopath, targetpath):
        pass

    def run(self):
        try:
            self.progress(self.isopath,self.targetpath)
        except StandardError:
            logging.exception('Could not update progress:')

if __name__ == "__main__":
    yinst()
