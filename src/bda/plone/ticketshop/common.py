from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import safe_unicode
from bda.plone.cart import CartDataProviderBase
from bda.plone.cart import CartItemStateBase
from bda.plone.cart import aggregate_cart_item_count
from bda.plone.cart import extractitems
from bda.plone.cart import get_item_stock
from bda.plone.cart import readcookie
from bda.plone.cart import get_object_by_uid
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.orders.common import OrderCheckoutAdapter
from bda.plone.ticketshop.interfaces import IBuyableEvent
from bda.plone.ticketshop.interfaces import IEventTickets
from bda.plone.ticketshop.interfaces import ISharedStock
from bda.plone.ticketshop.interfaces import ISharedStockData
from bda.plone.ticketshop.interfaces import ITicket
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData
from persistent.dict import PersistentDict
from plone.app.event.base import DT
from plone.app.event.recurrence import Occurrence
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


_ = MessageFactory('bda.plone.ticketshop')


class TicketShopCartDataProviderBase(CartDataProviderBase):

    def acquire_event(self, context):
        while not IBuyableEvent.providedBy(context):
            context = aq_parent(context)
        return context

    def related_tickets(self, ticket):
        pass

    def validate_count(self, uid, count):
        """Validate setting cart item count for uid.

        uid - Is the cart item UID.
        count - If count is 0, it means that a cart item is going to be
        deleted, which is always allowed. If count is > 0, it's the aggregated
        item count in cart.
        """
        count = float(count)
        if not count:
            return {'success': True, 'error': ''}
        cart_item = get_object_by_uid(self.context, uid)
        return {'success': True, 'error': ''}


@implementer(ICartItemDataProvider)
@adapter(ITicketOccurrence)
def TicketOccurrenceCartItemDataProviderProxy(context):
    return ICartItemDataProvider(aq_parent(context))


@adapter(ISharedStock, IBrowserRequest)
class TicketCartItemState(CartItemStateBase):

    @property
    def aggregated_count(self):
        items = extractitems(readcookie(self.request))
        stock_data = ISharedStockData(self.context)
        aggregated_count = 0
        for uid in stock_data.related_uids:
            aggregated_count += aggregate_cart_item_count(uid, items)
        return aggregated_count

    @property
    def completely_exceeded_alert(self):
        message = _(u'alert_ticket_no_longer_available',
                    default=u'Ticket is no longer available, please '
                            u'remove from cart')
        return translate(message, context=self.request)

    def partly_exceeded_alert(self, exceed):
        message = _(u'alert_ticket_number_exceed',
                    default=u'Limit exceed by ${exceed} tickets',
                    mapping={'exceed': int(exceed)})
        return translate(message, context=self.request)

    def number_reservations_alert(self, reserved):
        message = _(u'alert_ticket_number_reserved',
                    default=u'${reserved} tickets reserved',
                    mapping={'reserved': int(reserved)})
        return translate(message, context=self.request)

    def alert(self, count):
        stock = get_item_stock(self.context)
        available = stock.available
        if available is None:
            return ''
        reserved = self.reserved
        exceed = self.exceed
        if not reserved and not exceed:
            return ''
        if exceed:
            remaining_available = self.remaining_available
            if remaining_available > 0:
                return self.partly_exceeded_alert(exceed)
            return self.completely_exceeded_alert
        if reserved:
            return self.number_reservations_alert(reserved)
        return ''


class CatalogMixin(object):

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')


@implementer(IEventTickets)
class EventTicketsBase(object):

    def __init__(self, context):
        self.context = context

    @property
    def related_key(self):
        raise NotImplementedError(u"Abstract ``TicketData`` does not "
                                  u"implement ``related_key``")

    @property
    def related_uids(self):
        raise NotImplementedError(u"Abstract ``TicketData`` does not "
                                  u"implement ``related_uids``")


@adapter(ITicket)
class EventTickets(EventTicketsBase, CatalogMixin):

    @property
    def related_key(self):
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
class EventTicketOccurrences(EventTicketsBase, CatalogMixin):

    @property
    def related_key(self):
        return self.context.id

    @property
    def related_uids(self):
        event = aq_parent(aq_parent(self.context))
        brains = self.catalog(**{
            'portal_type': 'Ticket Occurrence',
            'path': '/'.join(event.getPhysicalPath()),
            'id': self.related_key,
        })
        return [brain.UID for brain in brains]


SHARED_STOCK_DATA_KEY = 'bda.plone.ticketshop.shared_stock'


@implementer(ISharedStockData)
class SharedStockData(EventTicketsBase):

    @property
    def shared_stock_context(self):
        raise NotImplementedError(u"Abstract ``SharedStockData`` does not "
                                  u"implement ``shared_stock_context``")

    @property
    def stock_data(self):
        annotations = IAnnotations(self.shared_stock_context, None)
        if annotations is None:
            # return dummy dict, prevents add form from raising an error
            return dict()
        data = annotations \
            and annotations.get(SHARED_STOCK_DATA_KEY, None) \
            or None
        if data is None:
            data = OOBTree()
            annotations[SHARED_STOCK_DATA_KEY] = data
        return data

    def get(self, field_name):
        return self.stock_data.get(self.related_key, {}).get(field_name)

    def set(self, field_name, value):
        stock_data = self.stock_data
        data = stock_data.setdefault(self.related_key, PersistentDict())
        if not value:
            data[field_name] = None
        else:
            data[field_name] = float(value)


@adapter(ITicket)
class TicketSharedStock(EventTickets, SharedStockData):

    @property
    def shared_stock_context(self):
        return aq_parent(self.context)


@adapter(ITicketOccurrence)
class TicketOccurrenceSharedStock(EventTicketOccurrences, SharedStockData):

    @property
    def shared_stock_context(self):
        return aq_parent(aq_parent(self.context))


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


class TicketOrderCheckoutAdapter(OrderCheckoutAdapter):
    """Custom ticket checkout adapter, which provides additional information on
    the product/event which is booked. The ticket itself is not enough to
    quickly identify it.
    """

    def create_booking(self, *args, **kwargs):
        booking = super(TicketOrderCheckoutAdapter,
                        self).create_booking(*args, **kwargs)
        event = self.context
        if ITicketOccurrence.providedBy(event):
            event = aq_parent(aq_parent(event))
        elif ITicket.providedBy(event):
            event = aq_parent(event)
        if IEvent.providedBy(event) or IOccurrence.providedBy(event):
            acc = IEventAccessor(event)
            lstart = ulocalized_time(
                DT(acc.start),
                long_format=True,
                context=event
            )
            lend = ulocalized_time(
                DT(acc.start),
                long_format=True,
                context=event
            )
            # XXX: no unicode, store as utf-8 encoded string instead
            booking.attrs['title'] = u'%s - %s (%s - %s)' % (
                safe_unicode(acc.title),
                safe_unicode(booking.attrs['title']),
                lstart,
                lend
            )
            # XXX: no unicode, store as utf-8 encoded string instead
            booking.attrs['eventtitle'] = acc.title
            booking.attrs['eventstart'] = acc.start
            booking.attrs['eventend'] = acc.end
        return booking
