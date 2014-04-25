from Products.CMFPlone.utils import getFSVersionTuple
from plone.app.testing import PLONE_FIXTURE
from bda.plone.ticketshop.interfaces import ITicketShopExtensionLayer
from plone.app.robotframework.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import z2
from zope.interface import alsoProvides


import plone.api


if getFSVersionTuple()[0] >= 5:
    PLONE5 = 1
else:
    PLONE5 = 0


def set_browserlayer(request):
    """Set the BrowserLayer for the request.

    We have to set the browserlayer manually, since importing the profile alone
    doesn't do it in tests.
    """
    alsoProvides(request, ITicketShopExtensionLayer)


class TicketshopLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bda.plone.ticketshop
        self.loadZCML(package=bda.plone.ticketshop,
                      context=configurationContext)

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'Products.DateRecurringIndex')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'bda.plone.ticketshop:default')

    def tearDownZope(self, app):
        # Uninstall old-style Products
        z2.uninstallProduct(app, 'Products.DateRecurringIndex')


Ticketshop_FIXTURE = TicketshopLayer()
Ticketshop_INTEGRATION_TESTING = IntegrationTesting(
    bases=(Ticketshop_FIXTURE,),
    name="Ticketshop:Integration")


class TicketshopATLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes,
                      context=configurationContext)

        import bda.plone.ticketshop
        self.loadZCML(package=bda.plone.ticketshop,
                      context=configurationContext)

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'Products.DateRecurringIndex')

        z2.installProduct(app, 'bda.plone.ticketshop.at')

    def setUpPloneSite(self, portal):
        if PLONE5:
            self.applyProfile(portal, 'Products.ATContentTypes:default')
        self.applyProfile(portal, 'bda.plone.ticketshop.at:default')

        portal.portal_workflow.setDefaultChain("one_state_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Create test users
        cru = plone.api.user.create
        cru(email="c1@test.com", username="customer1", password="customer1")
        cru(email="c2@test.com", username="customer2", password="customer2")
        cru(email="v1@test.com", username="vendor1", password="vendor1")
        cru(email="vendor2@test.com", username="vendor2", password="vendor2")

        # Create test content
        crc = plone.api.content.create

        crc(container=portal, type='Buyable Event', id='folder_1')
        crc(container=portal['folder_1'], type='Ticket', id='item_11',
            title="item_11")
        crc(container=portal['folder_1'], type='Ticket', id='item_12',
            title="item_12")

        crc(container=portal, type='Buyable Event', id='folder_2')
        crc(container=portal['folder_2'], type='Ticket', id='item_21',
            title="item_21")
        crc(container=portal['folder_2'], type='Ticket', id='item_22',
            title="item_22")


TicketshopAT_FIXTURE = TicketshopATLayer()
TicketshopAT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TicketshopAT_FIXTURE,),
    name="TicketshopAT:Integration")
TicketshopAT_ROBOT_TESTING = FunctionalTesting(
    bases=(
        MOCK_MAILHOST_FIXTURE,
        TicketshopAT_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name="TicketshopAT:Robot")
