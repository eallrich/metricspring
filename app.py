import json
import platform
import os
import time
import sys

import requests

import settings

host = platform.node()

def ns(prefix, key):
    """Namespace the key beneath the host and the given prefix"""
    return ".".join([host, prefix, key])


def loadavg():
    keys = ['1m', '5m', '15m']
    values = os.getloadavg()
    
    metrics = {ns('loadavg', k): v for k, v in zip(keys, values)}
    return metrics


def _prepare(metrics):
    now = int(time.time())
    data = []
    for metric, value in metrics.items():
        document = {
            'metric':    metric,
            'value':     value,
            'timestamp': now,
        }
        data.append(document)
    
    return json.dumps(data)


def send(metrics):
    headers = {
        'content-type': 'application/json',
    }
    payload = _prepare(metrics)
    
    for server in settings.servers:
        r = None
        try:
            r = requests.post(server, data=payload, headers=headers)
        except requests.exceptions.RequestException, err:
            print "RequestException against %s: %s" % (server, err)
        
        if r and not r.status_code == 201:
            print "Server %s returned status %d" % (server, r.status_code)
            print "    Text: %s" % r.text
        


start = used = 0
while True:
    start = int(time.time())
    send(loadavg())
    used = int(time.time()) - start
    time.sleep(60 - used) # sleep for the remainder of the minute

