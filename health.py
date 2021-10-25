import os
import re
from datetime import datetime
from os import uname
import requests


class Health():
    log = []
    journalctl = []

    def __init__(self):
        # armv7l - AP
        # x86_64 - ReSEA
        self.arc = uname().machine
        self.host = uname().nodename

    # Return packet loss in percents
    def ping(self, ip):
        try:
            ping = os.popen(f"ping -nc 4 -s 1400 {ip}")
            for s in ping:
                stat = re.search(r'\d{1,3}% packet loss', s)
                if stat:
                    return int(stat.group(0).split(' ')[0].replace('%', ''))
            return 100
        except:
            return 100

# 1a86:7523 - CH341 USB-COM adapter. Assembled at left side of mainboard.
# 0403:6001 - FTDI USB-COM adapter. Assembled at right side of mainboard.
# 10c4:ea60 - CP210x USB-COM adapter. Integrated to Maria.
# 0dd4:015d - Software printer on AP.
# 0dd4:01a8 - Software printer on SEA
# fff0:0100 - Exellio NFC
    def usb(self):
        device = {'validator': False, 'coin': False, 'printer': False, 'nfc': False}
        try:
            lsusb = os.popen("lsusb")
            for s in lsusb:
                id = s.split(' ')[5]
                if id == '1a86:7523':
                    device['coin'] = True
                if id == '0403:6001':
                    device['validator'] = True
                if id == '10c4:ea60' or id == '0dd4:015d' or id == '0dd4:01a8':
                    device['printer'] = True
                if id == 'fff0:0100':
                    device['nfc'] = True
            if self.arc == 'armv7l' and ( not device['validator'] or not device['coin']) or not device['printer']:
                dmesg = os.popen("dmesg")
                for s in dmesg:
                    if s.split(' ')[1] == 'usb':
                        self.log.append(s)
        except:
            pass
        return device

    # Return usage of disk space in percents
    def hdd(self):
        try:
            df = os.popen("df -h")
            for s in df:
                disk = re.split(r' +', s.strip())
                if disk[5] == '/':
                    return int(disk[4].replace('%', ''))
            return False
        except:
            # Root partition must be always mounted.
            # Running df is impossible and returns error if disk disconnected
            return False

    # Return total memory usage in percents
    def ram(self):
        meminfo = open('/proc/meminfo', 'r')
        for s in meminfo:
            ss = re.split(r' +', s.strip())
            if ss[0] == 'MemTotal:':
                total = int(ss[1])
            if ss[0] == 'MemFree:':
                free = int(ss[1])
        meminfo.close()
        return int((1-free/total)*100)

    # Return CPU usage in percents
    def cpu(self):
        loadavg = open('/proc/loadavg', 'r')
        avg = loadavg.readline().split(' ')[2].split('.')[0]
        loadavg.close()
        return int(avg)

    def api(self):
        try:
            r = requests.get('http://127.0.0.1:12345/api/v2/is-blocked/')
            if r.json().get('blocked', False):
                return r.json().get('reason', 'unknown')
            return 'ok'
        except:
            return 'down'

    def uptime(self):
        f = open('/proc/uptime', 'r')
        uptime = f.readline().split(' ')[0].split('.')[0]
        f.close()
        return int(uptime)

    def journal(self):
        try:
            f = os.popen("journalctl -u parkomat")
            current = f.readlines()
            if len(current) != len(self.journalctl):
                self.journalctl = current
                return current
            return []
        except:
            return []

    def all(self):
        self.log.clear()
        stat = dict()
        stat['time'] = datetime.now()
        stat['hdd'] = self.hdd()
        if stat['hdd']:
            stat['internet'] = self.ping('8.8.8.8')
            stat['vpn'] = self.ping('10.0.0.1')
            stat['uptime'] = self.uptime()
            stat['usb'] = self.usb()
            stat['cpu'] = self.cpu()
            stat['ram'] = self.ram()
            stat['api'] = self.api()
            stat['log'] = self.log
            stat['journal'] = self.journal()
        else:
            print(f"{stat['time']} WARNING!!! HDD disconnected!")
            # Ping not works without HDD. Just try to send alarm to server.
            stat['internet'] = 0
            for param in ('vpn', 'usb', 'uptime', 'cpu', 'ram', 'api', 'log', 'journal'):
                stat[param] = False
        return stat
