from persistent.dict import PersistentDict
from zope.interface import implementer
from zope.component import adapter
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from plone.event.interfaces import IRecurrenceSupport
from plone.app.event.recurrence import Occurrence
from bda.plone.cart.interfaces import ICartItemDataProvider
from .interfaces import (
    IBuyableEvent,
    ITicket,
    ITicketOccurrence,
    ISharedStockData,
    ITicketOccurrenceData,
)


@implementer(ICartItemDataProvider)
@adapter(ITicketOccurrence)
def TicketOccurrenceCartItemDataProviderProxy(context):
    return ICartItemDataProvider(aq_parent(context))


class CatalogMixin(object):

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')


SHARED_STOCK_DATA_KEY = 'bda.plone.ticketshop.shared_stock'


@implementer(ISharedStockData)
class SharedStockData(object):

    def __init__(self, context):
        self.context = context

    @property
    def shared_stock_context(self):
        raise NotImplementedError(u"Abstract ``SharedStockData`` does not "
                                  u"implement ``shared_stock_context``")

    @property
    def shared_stock_key(self):
        raise NotImplementedError(u"Abstract ``SharedStockData`` does not "
                                  u"implement ``shared_stock_key``")

    @property
    def related_uids(self):
        raise NotImplementedError(u"Abstract ``SharedStockData`` does not "
                                  u"implement ``related_uids``")

    @property
    def stock_data(self):
        annotations = IAnnotations(self.shared_stock_context)
        data = annotations.get(SHARED_STOCK_DATA_KEY, None)
        if data is None:
            data = OOBTree()
            annotations[SHARED_STOCK_DATA_KEY] = data
        return data

    def get(self, field_name):
        return self.stock_data.get(self.shared_stock_key, {}).get(field_name)

    def set(self, field_name, value):
        stock_data = self.stock_data
        data = stock_data.setdefault(self.shared_stock_key, PersistentDict())
        if not value:
            data[field_name] = None
        else:
            data[field_name] = float(value)


@adapter(ITicket)
class TicketSharedStock(SharedStockData, CatalogMixin):

    @property
    def shared_stock_context(self):
        return aq_parent(self.context)

    @property
    def shared_stock_key(self):
        return 'canonical_tickets'

    @property
    def related_uids(self):
        event = aq_parent(self.context)
        brains = self.catalog(**{
            'portal_type': 'Ticket',
            'path': '/'.join(event.getPhysicalPath()),
        })
        return [brain.UID for brain in brains]


@adapter(ITicketOccurrence)
class TicketOccurrenceSharedStock(SharedStockData, CatalogMixin):

    @property
    def shared_stock_context(self):
        return aq_parent(aq_parent(self.context))

    @property
    def shared_stock_key(self):
        return self.context.id

    @property
    def related_uids(self):
        event = aq_parent(aq_parent(self.context))
        brains = self.catalog(**{
            'portal_type': 'Ticket Occurrence',
            'path': '/'.join(event.getPhysicalPath()),
            'id': self.shared_stock_key,
        })
        return [brain.UID for brain in brains]


@implementer(ITicketOccurrenceData)
@adapter(IBuyableEvent)
class TicketOccurrenceData(CatalogMixin):

    def __init__(self, context):
        self.context = context

    @property
    def tickets(self):
        brains = self.catalog(**{
            'portal_type': 'Ticket',
            'path': '/'.join(self.context.getPhysicalPath()),
        })
        return [brain.getObject() for brain in brains]

    def ticket_occurrences(self, occurrence_id):
        brains = self.catalog(**{
            'id': occurrence_id,
            'portal_type': 'Ticket Occurrence',
            'path': '/'.join(self.context.getPhysicalPath()),
        })
        return [brain.getObject() for brain in brains]

    def _copy_field_value(self, ticket, ticket_occurrence, field_name):
        ticket_field = ticket.getField(field_name)
        value = ticket_field.getAccessor(ticket)()
        ticket_occurrence_field = ticket_occurrence.getField(field_name)
        mutator = ticket_occurrence_field.getMutator(ticket_occurrence)
        mutator(value)

    def create_ticket_occurrences(self):
        tickets = self.tickets
        recurrence = IRecurrenceSupport(self.context)
        for occurrence in recurrence.occurrences():
            if not isinstance(occurrence, Occurrence):
                continue
            for ticket in tickets:
                if occurrence.id in ticket.objectIds():
                    continue
                ticket.invokeFactory(
                    'Ticket Occurrence',
                    occurrence.id,
                    title=ticket.Title())
                ticket_occurrence = ticket[occurrence.id]
                self._copy_field_value(
                    ticket, ticket_occurrence, 'item_available')
                self._copy_field_value(
                    ticket, ticket_occurrence, 'item_overbook')
                ticket_occurrence.reindexObject()
