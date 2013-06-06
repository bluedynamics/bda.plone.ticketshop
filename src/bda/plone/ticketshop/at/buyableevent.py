from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes import atapi
from collectice.folderishtypes.content.folderish_event import FolderishEvent
from ..interfaces import IBuyableEvent
from ..config import PROJECTNAME
from .. import _


schema = atapi.Schema((
))


BuyableEvent_schema = FolderishEvent.schema.copy() + schema.copy()


class BuyableEvent(FolderishEvent):
    security = ClassSecurityInfo()
    implements(IBuyableEvent)
    meta_type = 'BuyableEvent'
    _at_rename_after_creation = True
    schema = BuyableEvent_schema
    exclude_from_nav = False


atapi.registerType(BuyableEvent, PROJECTNAME)
