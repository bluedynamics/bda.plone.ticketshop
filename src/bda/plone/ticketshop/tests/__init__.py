from zope.interface import alsoProvides
from plone.app.testing import (
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from bda.plone.ticketshop.interfaces import ITicketShopExtensionLayer


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

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'bda.plone.ticketshop:default')

    def tearDownZope(self, app):
        pass


Ticketshop_FIXTURE = TicketshopLayer()
Ticketshop_INTEGRATION_TESTING = IntegrationTesting(
    bases=(Ticketshop_FIXTURE,),
    name="Ticketshop:Integration")
