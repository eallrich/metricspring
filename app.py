import platform
import os
import time

from statsd import StatsClient

host = platform.node()

statsd = StatsClient(prefix=host)

def ns(*args):
    """Create a metric key from the given strings"""
    return ".".join(args)


def loadavg():
    keys = ['1m', '5m', '15m']
    values = os.getloadavg()
    
    metrics = {ns('loadavg', k): v for k, v in zip(keys, values)}
    
    for metric, value in metrics.items():
        statsd.gauge(metric, value)


start = used = 0
metric = ns('metricspring', 'gathering')
while True:
    start = int(time.time())
    with statsd.timer(metric):
        loadavg()
    used = int(time.time()) - start
    try:
        time.sleep(10 - used) # sleep for the remainder of the interval
    except IOError as exc:
        print "IOError on time.sleep(10 - %r): %s" % (used, exc)
        # Default sleep after an error
        time.sleep(8)

