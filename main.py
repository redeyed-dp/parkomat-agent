from health import Health
from models import db, HealthCache
from time import sleep
from os import uname
import json
import requests

def sendToServer(data, host):
    data['host'] = host
    data['time'] = str(data['time'])
    try:
#        print(json.dumps(data))
#        r = requests.post(url='https://api-parking.icity.com.ua/api/v1/log/', json=json.dumps(data))
        r = requests.post(url='http://116.203.249.22:8888/', json=json.dumps(data))
#        print("raise: {}".format(r.raise_for_status()))
#        print("status: {}".format(r.status_code))
        return True
    except:
        return False

def monitoring():
    # Define hostname once. Are this function works while SSD disconnected?
    host = uname().nodename
    db.connect()
    try:
        HealthCache.notEmpty()
    except:
        db.create_tables([HealthCache])
    health = Health()
    while True:
        # Get current state
        stat = health.all()
        # Read from cache and try to send
        try:
            if stat.get('internet') == 0 and HealthCache.notEmpty():
                print("Old probes found in cache. Trying to send.")
                for probe in HealthCache.select().order_by(HealthCache.time):
                    old = dict()
                    for param in ('time', 'internet', 'vpn', 'usb', 'cpu', 'ram', 'hdd', 'api', 'log'):
                        old[param] = getattr(probe, param)
                    if sendToServer(data=old, host=host):
                        probe.delete_instance()
        except:
            pass

        sendToServer(data=stat, host=host)
        # Save to cache if packet loss in main channel greater than 0%
        if stat.get('internet') == 100:
            try:
                probe = HealthCache.create(time=stat['time'], internet=stat['internet'], vpn=stat['vpn'],
                                           usb=stat['usb'], cpu=stat['cpu'], ram=stat['ram'], hdd=stat['hdd'],
                                           api=stat['api'], log=stat['log'])
                probe.save()
            except:
                pass
        sleep(50)

monitoring()