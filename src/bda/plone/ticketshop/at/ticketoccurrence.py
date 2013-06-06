from AccessControl import ClassSecurityInfo
from zope.interface import implementer
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.shop.interfaces import IBuyable
from ..interfaces import ITicketOccurrence
from ..config import PROJECTNAME
from .. import _


schema = atapi.Schema((
))


TicketOccurrence_schema = atapi.BaseFolderSchema.copy() + schema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseFolder, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    portal_type = 'Ticket Occurrence'
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True


atapi.registerType(TicketOccurrence, PROJECTNAME)
