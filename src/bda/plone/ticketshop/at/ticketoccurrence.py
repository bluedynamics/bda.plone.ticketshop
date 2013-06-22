from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.shop.interfaces import IBuyable
from plone.event.utils import pydt
from plone.formwidget.datetime.at import DatetimeWidget
from zope.interface import implementer
from ..interfaces import ITicketOccurrence
from ..config import PROJECTNAME


schema = atapi.Schema((
))


TicketOccurrence_schema = atapi.BaseSchema.copy() + schema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseContent, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    portal_type = 'Ticket Occurrence'
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True


atapi.registerType(TicketOccurrence, PROJECTNAME)
