import pytest
from mock import patch
from twisted.trial.unittest import TestCase
from twisted.internet import protocol, reactor, defer
from twisted.python import log

from raven import base
from raven.contrib import twisted


class TempStoreClient(base.Client):

    def __init__(self, servers=None, **kwargs):
        self.events = []
        super(TempStoreClient, self).__init__(servers=servers, **kwargs)

    def is_enabled(self):
        return True

    def send(self, **kwargs):
        self.events.append(kwargs)


client = TempStoreClient()




class TwistedTestCase(TestCase):

    #@patch('raven.base.Client', **{'return_value': client})
    #@twisted.observe('http://a:b@test.sentry.com/api/3')
    def setUp(self, *args):
        def test(event):
            pytest.set_trace()
        log.addObserver(test)

    def test_raven(self):
        x = defer.Deferred()
        x.errback()
        return x
