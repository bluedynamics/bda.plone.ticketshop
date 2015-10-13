from bda.plone.ticketshop.tests import Ticketshop_INTEGRATION_TESTING
from bda.plone.ticketshop.tests import set_browserlayer
import unittest2 as unittest


class TestTicketshop(unittest.TestCase):
    layer = Ticketshop_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

    def test_foo(self):
        self.assertEquals(1, 1)
