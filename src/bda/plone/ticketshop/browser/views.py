from Acquisition import aq_parent
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.event.browser.event_view import EventView
from bda.plone.cart import get_item_availability
from bda.plone.shop.at import field_value
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData


class TicketsViewlet(ViewletBase):
    index = ViewPageTemplateFile('tickets_viewlet.pt')


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
    def tickets(self):
        raise NotImplementedError(u"Abstract SharedStockBuyableViewletBase "
                                  u"does not implement tickets")


class BuyableEventTickets(SharedStockBuyables):

    @property
    def tickets(self):
        if not hasattr(self.request, '_tickets'):
            data = ITicketOccurrenceData(self.context)
            self.request._tickets = data.tickets
        return self.request._tickets


class BuyableEventOccurrenceTickets(SharedStockBuyables):

    @property
    def tickets(self):
        if not hasattr(self.request, '_tickets'):
            data = ITicketOccurrenceData(aq_parent(self.context))
            self.request._tickets = data.ticket_occurrences(self.context.id)
        return self.request._tickets


class TicketView(BrowserView):

    @property
    def available(self):
        return field_value(self.context, 'item_available')

    @property
    def overbook(self):
        return field_value(self.context, 'item_overbook')


class TicketOccurrenceView(BrowserView):

    @property
    def available(self):
        return field_value(self.context, 'item_available')

    @property
    def overbook(self):
        return field_value(self.context, 'item_overbook')
