from Acquisition import aq_parent
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.cart import ascur
from bda.plone.cart import get_item_availability
from bda.plone.orders.browser import views
from bda.plone.shop.at import field_value
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.uuid.utils import uuidToObject
from plone.event.interfaces import IEvent

from ..interfaces import ITicket
from ..interfaces import ITicketOccurrence
from ..interfaces import ITicketOccurrenceData


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
