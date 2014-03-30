from Acquisition import aq_parent
from Products.Five import BrowserView
from bda.plone.cart import ascur
from bda.plone.orders.browser import views
from bda.plone.shop.at import field_value
from bda.plone.ticketshop.interfaces import ITicket
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from plone.app.uuid.utils import uuidToObject
from plone.event.interfaces import IEvent
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


def _get_booking_url(booking):
    booking_obj = uuidToObject(booking.attrs['buyable_uid'])
    url = booking_obj.absolute_url()
    if ITicketOccurrence.providedBy(booking_obj):
        # assumption1: ticketoccurrence id = occurrence id
        # assumption2: ticketoccurrence parent = ticket
        occurrence_id = booking_obj.id
        event = aq_parent(aq_parent(booking_obj))
        if IEvent.providedBy(event):
            url = '%s/%s' % (
                event.absolute_url(),
                occurrence_id
            )

    elif ITicket.providedBy(booking_obj):
        event = aq_parent(booking_obj)
        if IEvent.providedBy(event):
            url = event.absolute_url()
    return url


class OrderView(views.OrderView):

    @property
    def listing(self):
        ret = list()
        for booking in self.order_data.bookings:
            url = _get_booking_url(booking)
            ret.append({
                'title': booking.attrs['title'],
                'url': url,
                'count': booking.attrs['buyable_count'],
                'net': ascur(booking.attrs.get('net', 0.0)),
                'vat': booking.attrs.get('vat', 0.0),
                'exported': booking.attrs['exported'],
                'comment': booking.attrs['buyable_comment'],
                'quantity_unit': booking.attrs.get('quantity_unit'),
                'currency': booking.attrs.get('currency'),
            })
        return ret


class ExportOrdersForm(views.ExportOrdersForm):

    def export_val(self, record, attr_name):
        if attr_name == 'url':
            return _get_booking_url(record)
        super(ExportOrdersForm, self).export_val(record, attr_name)
