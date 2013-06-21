from Acquisition import aq_parent
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.event.browser.event_view import EventView
from bda.plone.shop.at import field_value
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData


class BuyableEventViewlet(ViewletBase):
    index = ViewPageTemplateFile('tickets.pt')

    @property
    def tickets(self):
        print 'BuyableEventViewlet'
        data = ITicketOccurrenceData(self.context)
        print data.tickets
        print '---'
        return data.tickets


class BuyableEventOccurrenceViewlet(ViewletBase):
    index = ViewPageTemplateFile('tickets.pt')

    @property
    def tickets(self):
        print 'BuyableEventOccurrenceViewlet'
        data = ITicketOccurrenceData(aq_parent(self.context))
        print data.ticket_occurrences(self.context.id)
        print '---'
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
