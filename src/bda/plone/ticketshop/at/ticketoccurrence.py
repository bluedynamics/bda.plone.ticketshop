# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.orders.interfaces import IBuyable
from bda.plone.ticketshop.at import PROJECTNAME
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from zope.interface import implementer

TicketOccurrence_schema = atapi.BaseSchema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseContent, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    meta_type = 'Ticket Occurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True


atapi.registerType(TicketOccurrence, PROJECTNAME)
