#! /usr/bin/python

import os

__author__="hechao"
__date__ ="$2011-6-8 14:43:13$"

global version,appdirname
version = "5.0"
appdirname="yinst"

homedir = os.path.expanduser("~")
if not os.path.exists('%s/%s' % (homedir, appdirname)) or not os.path.isdir('%s/%s' % (homedir,appdirname)):
    os.system('mkdir ~/%s' % appdirname)

configdir = '%s/%s'  % (homedir,appdirname)

SOURCE_CD, SOURCE_ISO, SOURCE_IMG = range(3)
