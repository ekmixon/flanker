
import logging
import os
import time
from contextlib import contextmanager

_client = None
_log = logging.getLogger(__name__)


def init():
    global _client

    statsd_host = os.environ.get('FLANKER_METRICS_HOST')
    statsd_port = os.environ.get('FLANKER_METRICS_PORT')
    statsd_prfx = os.environ.get('FLANKER_METRICS_PREFIX')

    if not statsd_host or not statsd_port or not statsd_prfx:
        return

    try:
        import statsd
    except ImportError:
        return

    _client = statsd.StatsClient(statsd_host, statsd_port, prefix=statsd_prfx)


def incr(key, increment=1):
    global _client
    if _client:
        if increment < 0:
            _client.decr(key, increment)
        else:
            _client.incr(key, increment)
    elif _client is None:
        _client = False
        init()
        incr(key, increment)


@contextmanager
def timer(metric_name):
    if _client:
        t = time.time()
        yield
        _client.timing(metric_name, (time.time() - t) * 1000, 1)
    else:
        yield
