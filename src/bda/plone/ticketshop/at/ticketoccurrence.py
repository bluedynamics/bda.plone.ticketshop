from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.shop.interfaces import IBuyable
from zope.interface import implementer
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from bda.plone.ticketshop.config import PROJECTNAME

TicketOccurrence_schema = atapi.BaseSchema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseContent, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True


atapi.registerType(TicketOccurrence, PROJECTNAME)
