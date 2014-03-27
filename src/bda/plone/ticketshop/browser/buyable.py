from Acquisition import aq_parent
from Products.Five import BrowserView
from bda.plone.cart import get_item_availability
from plone.app.layout.viewlets.common import ViewletBase

from ..interfaces import ITicketOccurrenceData


class BuyableViewlet(ViewletBase):
    pass


class SharedStockBuyables(BrowserView):

    @property
    def listen_uid_css(self):
        classes = list()
        for ticket in self.tickets:
            classes.append('cart_item_%s' % ticket.UID())
        return ' '.join(classes)

    @property
    def _item_availability(self):
        return get_item_availability(self.tickets[0], self.request)

    @property
    def availability_signal(self):
        return self._item_availability.signal

    @property
    def availability_details(self):
        return self._item_availability.details

    @property
    def ticket_context(self):
        raise NotImplementedError(u"Abstract SharedStockBuyableViewletBase "
                                  u"does not implement ticket context")

    @property
    def tickets(self):
        raise NotImplementedError(u"Abstract SharedStockBuyableViewletBase "
                                  u"does not implement tickets")


class BuyableEventTickets(SharedStockBuyables):

    @property
    def ticket_context(self):
        return self.context

    @property
    def tickets(self):
        if not hasattr(self.request, '_tickets'):
            data = ITicketOccurrenceData(self.ticket_context)
            self.request._tickets = data.tickets
        return self.request._tickets


class BuyableEventOccurrenceTickets(SharedStockBuyables):

    @property
    def ticket_context(self):
        return aq_parent(self.context)

    @property
    def tickets(self):
        if not hasattr(self.request, '_tickets'):
            occurrence_id = self.context.id
            data = ITicketOccurrenceData(self.ticket_context)
            self.request._tickets = data.ticket_occurrences(occurrence_id)
        return self.request._tickets


class BuyableTicketTickets(BuyableEventTickets):

    @property
    def ticket_context(self):
        return aq_parent(self.context)


class BuyableTicketOccurrenceTickets(BuyableEventOccurrenceTickets):

    @property
    def ticket_context(self):
        return aq_parent(aq_parent(self.context))
