#! /usr/bin/python

import subprocess
import logging
import logging.handlers
import os
import gio

MAX_LOG_SIZE = 1024 * 1024 * 1
MAX_LOG_BACKUP = 0

__author__="hechao"
__date__ ="$2011-6-8 15:18:52$"

def set_logger():
    log = logging.getLogger('')
    cache_dir = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
    log_file = os.path.join(cache_dir, 'yinst.log')
    handler = None
    try:
        handler = logging.handlers.RotatingFileHandler(log_file,
                     maxBytes=MAX_LOG_SIZE, backupCount=MAX_LOG_BACKUP)
    except IOError:
        logging.exception('Could not set up file logging:')
    if handler:
        formatter = logging.Formatter('%(asctime)s (%(levelname)s)'' %(filename)s:%(lineno)d: %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)
    log.setLevel(logging.DEBUG)

def popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
          stdin=subprocess.PIPE):
    logging.debug(str(cmd))

    process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, stdin=stdin,
                               startupinfo=None)
    out, err = process.communicate()
    if process.returncode is None:
        process.wait()
    elif process.returncode != 0:
        raise Exception(err)
    return out

def get_gnome_drive(self, dev):
    try:
        monitor = gio.volume_monitor_get()
        for drive in monitor.get_volumes():
            if 'unix-device' in drive.enumerate_identifiers():
                if drive.get_identifier('unix-device') == dev:
                    name = drive.get_name()
                    icon = drive.get_icon().get_names()[0]
                    return (name, icon)
        for drive in monitor.get_connected_drives():
            if 'unix-device' in drive.enumerate_identifiers():
                if drive.get_identifier('unix-device') == dev:
                    name = drive.get_name()
                    icon = drive.get_icon().get_names()[0]
                    return (name, icon)
    except Exception:
        logging.exception('Could not determine GNOME drive:')
    return ('', '')

def format_size(size):
    if size < 1024:
        unit = 'B'
        factor = 1
    elif size < 1024 * 1024:
        unit = 'kB'
        factor = 1024
    elif size < 1024 * 1024 * 1024:
        unit = 'MB'
        factor = 1024 * 1024
    elif size < 1024 * 1024 * 1024 * 1024:
        unit = 'GB'
        factor = 1024 * 1024 * 1024
    else:
        unit = 'TB'
        factor = 1024 * 1024 * 1024 * 1024
    return '%.1f %s' % (float(size) / factor, unit)