#! /usr/bin/env python
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

YINST_IFACE = 'com.startos.yinst'
YINST_PATH = '/com/startos/yinst'
root_dir = os.path.abspath(os.path.dirname(__file__))

class linst(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(YINST_IFACE, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, YINST_PATH)
        self.dbus_info = None
        self.polkit = None

    @dbus.service.method(YINST_IFACE,in_signature='',out_signature='',sender_keyword='sender')
    def exit(self,sender=None):
	self.check_polkit(sender)

    @dbus.service.method(YINST_IFACE,in_signature='',out_signature='',sender_keyword='sender')
    def write_file(self, isopath, flag, locale, initrd, filename, sender=None):
        self.check_polkit(sender)
        template_file = "%s/10_livecd" %root_dir
        template = self.read_file(template_file)
        dic = dict(iso_path = isopath,flags = flag,locale = locale,initrds = initrd)
        content = template
        for k,v in dic.items():
            k = "$(%s)" % k
            content = content.replace(k, v)

        f = open(filename,'w+')
        f.write(content)
        f.close()
        os.chmod(filename,0766)
        os.system("update-grub")
        sys.exit()

    def read_file(self,file_path):
        f = open(file_path, 'r')
        content = f.read()
        f.close()
        return content

    def check_polkit(self,sender):
        
        if not sender: raise ValueError('sender == None')
        logging.info("sender == %s" %sender)
	
        obj = dbus.SystemBus().get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
        obj = dbus.Interface(obj, 'org.freedesktop.PolicyKit1.Authority')
        (granted, _, details) = obj.CheckAuthorization(
                ('system-bus-name', {'name': sender}), 'com.startos.yinst', {}, dbus.UInt32(1), '', timeout=36000)
        logging.debug("details == %s" %details)
        if not granted:
            logging.debug('_check_polkit_privilege: sender %s on connection %s ' %(sender,str(details)))
	    sys.exit()

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    conf = linst()
    loop = gobject.MainLoop()
    loop.run()
