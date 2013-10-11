import sys
from functools import wraps
from urlparse import urlparse, urlunparse

import raven
from twisted.python import log


def observe(sentry_dsn):
    ''' Decorator adding twisted raven client and blocking client if reactor
    is not yet running.
    :param str sentry_dsn: URL of sentry API
    '''

    # create blocking client:
    raven_client = raven.base.Client(sentry_dsn)

    # add twisted logObserver with twisted raven client:
    observer = get_observer(sentry_dsn)
    if observer:
        log.addObserver(observer)

    import pytest; pytest.set_trace()
    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            ''' Calls original function, catches any exception, sends it
            to sentry and re-raises it again. '''
            try:
                return function(*args, **kwargs)
            except:
                raven_client.captureException(sys.exc_info())
                raise  # re-raise caught exception
        return wrapper

    return decorator


def get_observer(sentry_dsn):
    '''
    Returns twisted's logObserver that catches twisted Failures and sends them
    to sentry using non-blocking transport.
    '''

    # force using 'twisted' raven transport:
    dsn = list(urlparse(sentry_dsn))
    dsn[0] = 'twisted+' + dsn[0]
    dsn_twisted = urlunparse(dsn)

    try:
        raven_client = raven.base.Client(dsn_twisted)
    except ValueError:
        # `sentry_dsn` is not correct address
        return None

    def raven_observer(event):
        '''
        :param dict event: Twisted eventDict from twisted.python.log
        '''
        if not event['isError']:
            return

        failure = event.get('failure')
        if not failure:
            return raven_client.captureMessage(event['message'])

        exc_info = failure.type, failure.value, failure.tb
        raven_client.captureException(exc_info)

    return raven_observer
