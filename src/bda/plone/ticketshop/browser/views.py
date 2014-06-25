from Acquisition import aq_parent
from Products.Five import BrowserView
from bda.plone.cart import get_object_by_uid
from bda.plone.orders.browser.views import COMPUTED_BOOKING_EXPORT_ATTRS
from bda.plone.shop.at import field_value
from bda.plone.ticketshop.interfaces import ITicket
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from plone.app.event.browser.event_summary import EventSummaryView
from plone.event.interfaces import IEvent


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


def _get_event_url(ticket):
    """Return the URL to an event or event occurrence for a ticket or ticket
    occurrence.
    """

    url = ticket.absolute_url()

    if ITicketOccurrence.providedBy(ticket):
        # assumption1: ticketoccurrence id = occurrence id
        # assumption2: ticketoccurrence parent = ticket
        event = aq_parent(aq_parent(ticket))
        if IEvent.providedBy(event):
            url = '{}/{}'.format(
                event.absolute_url(),
                ticket.id
            )

    elif ITicket.providedBy(ticket):
        event = aq_parent(ticket)
        if IEvent.providedBy(event):
            url = event.absolute_url()

    return url


def event_url(context, booking):
    """Function for COMPUTED_BOOKING_EXPORT_ATTRS to return a url for a given
    context object and booking record.
    """
    obj = get_object_by_uid(context, booking.attrs['buyable_uid'])
    if obj:
        return _get_event_url(obj)
    return None


# Add the URL of the event to the CSV export parameter
COMPUTED_BOOKING_EXPORT_ATTRS['event_url'] = event_url
