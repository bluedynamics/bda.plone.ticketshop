# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.orders.interfaces import IBuyable
from bda.plone.ticketshop.at import PROJECTNAME
from bda.plone.ticketshop.interfaces import ITicket
from zope.interface import implementer

Ticket_schema = atapi.BaseFolderSchema.copy()


@implementer(ITicket, IBuyable)
class Ticket(atapi.BaseFolder, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    meta_type = 'Ticket'
    _at_rename_after_creation = True
    schema = Ticket_schema
    exclude_from_nav = True


atapi.registerType(Ticket, PROJECTNAME)
