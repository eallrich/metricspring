import json
import platform
import os
import time
import sys

import requests
from statsd import StatsClient

import settings

host = platform.node()

statsd = StatsClient()

def ns(prefix, key):
    """Namespace the key beneath the host and the given prefix"""
    return ".".join([host, prefix, key])


def loadavg():
    keys = ['1m', '5m', '15m']
    values = os.getloadavg()
    
    metrics = {ns('loadavg', k): v for k, v in zip(keys, values)}
    
    for metric, value in metrics.items():
        statsd.gauge(metric, value)
    
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
        try:
            r = requests.post(server, data=payload, headers=headers)
            if r.status_code != 201:
                print "Server %s returned status %d; text:" % (server, r.status_code)
                print r.text
        except requests.exceptions.RequestException as exc:
            print "RequestException against %s: %s" % (server, exc)


start = used = 0
metric = ns('metricspring', 'gathering')
while True:
    start = int(time.time())
    with statsd.timer(metric):
        send(loadavg())
    used = int(time.time()) - start
    try:
        time.sleep(60 - used) # sleep for the remainder of the minute
    except IOError as exc:
        print "IOError on time.sleep(60 - %r): %s" % (used, exc)
        # Default sleep
        time.sleep(55)

