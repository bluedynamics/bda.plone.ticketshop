from Acquisition import aq_parent
from Products.Five import BrowserView
from bda.plone.shop.at import field_value
from plone.app.event.browser.event_summary import EventSummaryView


class EventTicketSummaryView(EventSummaryView):

    def __init__(self, request, response):
        super(EventTicketSummaryView, self).__init__(request, response)
        self.excludes = ['subjects', 'occurrences', 'ical']


class TicketView(BrowserView):

    @property
    def available(self):
        return field_value(self.context, 'item_available')

    @property
    def overbook(self):
        return field_value(self.context, 'item_overbook')

    @property
    def event_context(self):
        return aq_parent(self.context)

    def event_summary(self):
        return self.event_context.restrictedTraverse(
            '@@event_ticket_summary')()


class TicketOccurrenceView(TicketView):

    @property
    def event_context(self):
        return aq_parent(aq_parent(self.context))
