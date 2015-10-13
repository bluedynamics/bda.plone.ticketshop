from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from bda.plone.ticketshop.at import PROJECTNAME
from bda.plone.ticketshop.interfaces import IBuyableEvent
from collective.folderishtypes.content.folderish_event import FolderishEvent
from zope.interface import implementer

BuyableEvent_schema = FolderishEvent.schema.copy()


@implementer(IBuyableEvent)
class BuyableEvent(FolderishEvent):
    security = ClassSecurityInfo()
    meta_type = 'Buyable Event'
    _at_rename_after_creation = True
    schema = BuyableEvent_schema
    exclude_from_nav = False


atapi.registerType(BuyableEvent, PROJECTNAME)
