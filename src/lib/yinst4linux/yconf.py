#! /usr/bin/python
#coding=utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

#__author__="hechao"
#__date__ ="$2011-6-20 17:47:50$"

import gobject
import dbus
import dbus.service
import os
import sys
import dbus.mainloop.glib
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='/tmp/yinst.log')

YINST_IFACE = 'com.ylmf.yinst'
YINST_PATH = '/com/ylmf/yinst'
root_dir = os.path.abspath(os.path.dirname(__file__))

class linst(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(YINST_IFACE, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, YINST_PATH)
        self.dbus_info = None
        self.polkit = None

    @dbus.service.method(YINST_IFACE)
    def write_file(self,isopath, locale, filename):

        template_file = "%s/05_livecd" %root_dir
        template = self.read_file(template_file)
        logging.debug("template_file %s" %template_file)
        dic = dict(iso_path = isopath,locale = locale)
        content = template
        for k,v in dic.items():
            k = "$(%s)" % k
            content = content.replace(k, v)

        f = open(filename,'w+')
        f.write(content)
        f.close()
        os.system("chmod +x %s" %filename)
        os.system("update-grub")
        logging.debug("update-grub")
        #sys.exit()

    def read_file(self,file_path):
        f = open(file_path, 'r')
        content = f.read()
        f.close()
        return content

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    conf = linst()
    loop = gobject.MainLoop()
    loop.run()
