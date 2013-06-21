from Acquisition import aq_parent
from Products.Five import BrowserView
from plone.app.event.browser.event_view import EventView
from bda.plone.shop.at import field_value
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData


class BuyableEventView(EventView):

    @property
    def tickets(self):
        data = ITicketOccurrenceData(self.context)
        return data.tickets


class BuyableEventOccurrenceView(EventView):

    @property
    def tickets(self):
        data = ITicketOccurrenceData(aq_parent(self.context))
        return data.ticket_occurrences(self.context.id)


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
