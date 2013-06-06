from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from ..interfaces import ITicket
from ..config import PROJECTNAME
from .. import _


schema = atapi.Schema((
))


Ticket_schema = atapi.BaseFolderSchema.copy() + schema.copy()


class Ticket(atapi.BaseFolder, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    implements(ITicket)
    meta_type = 'Ticket'
    _at_rename_after_creation = True
    schema = Ticket_schema
    exclude_from_nav = False


atapi.registerType(Ticket, PROJECTNAME)
