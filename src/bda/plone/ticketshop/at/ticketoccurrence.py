from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from ..interfaces import ITicketOccurrence
from ..config import PROJECTNAME
from .. import _


schema = atapi.Schema((
))


TicketOccurrence_schema = atapi.BaseFolderSchema.copy() + schema.copy()


class TicketOccurrence(atapi.BaseFolder, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    implements(ITicketOccurrence)
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True


atapi.registerType(TicketOccurrence, PROJECTNAME)
