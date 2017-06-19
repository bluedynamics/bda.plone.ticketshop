from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import safe_unicode
from bda.plone.cart import CartItemStateBase
from bda.plone.cart import aggregate_cart_item_count
from bda.plone.cart import extractitems
from bda.plone.cart import get_catalog_brain
from bda.plone.cart import get_item_data_provider
from bda.plone.cart import get_item_state
from bda.plone.cart import get_item_stock
from bda.plone.cart import get_object_by_uid
from bda.plone.cart import readcookie
from bda.plone.cart.interfaces import ICartItemDataProvider
from bda.plone.orders.common import OrderCheckoutAdapter
from bda.plone.shop import message_factory as bps_
from bda.plone.shop.cartdata import CartDataProvider
from bda.plone.ticketshop.interfaces import IBuyableEvent
from bda.plone.ticketshop.interfaces import IBuyableEventData
from bda.plone.ticketshop.interfaces import IEventTickets
from bda.plone.ticketshop.interfaces import ISharedBuyablePeriodData
from bda.plone.ticketshop.interfaces import ISharedData
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
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

try:
    # pae's AT branch is optional and gone in pae 2.0
    from plone.app.event.at.interfaces import IATEvent
    from plone.app.event.at.traverser import OccurrenceTraverser as OccTravAT
except ImportError:
    class IATEvent(Interface):
        pass

from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.traverser import OccurrenceTraverser as OccTravDX


_ = MessageFactory('bda.plone.ticketshop')


def ticket_title_generator(obj):
    """Generate a title for the ticket, also using event information.
    """

    event = obj
    ret = {
        'title': obj.title, 'eventtitle': '', 'eventstart': '', 'eventend': ''
    }

    if ITicketOccurrence.providedBy(event):
        event = aq_parent(aq_parent(event))
        # Traverse to the Occurrence object
        if IATEvent.providedBy(event):
            # get the request out of thin air to be able to publishTraverse to
            # the transient Occurrence object.
            traverser = OccTravAT(event, getRequest())
        elif IDXEvent.providedBy(event):
            # TODO
            traverser = OccTravDX(event, getRequest())
        else:
            raise NotImplementedError(
                u"There is no event occurrence traverser implementation for "
                u"this kind of object."
            )
        try:
            event = traverser.publishTraverse(getRequest(), obj.id)
        except KeyError:
            # Maybe the ticket occurrence isn't valid anymore because the
            # event occurence doesn't exist anymore.
            # Just ignore that case.
            return ret

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
        ret = dict(
            title=u'%s - %s (%s - %s)' % (
                safe_unicode(acc.title),
                safe_unicode(obj.title),
                lstart,
                lend,
            ),
            eventtitle=acc.title,
            eventstart=acc.start,
            eventend=acc.end,
        )
    return ret


class TicketShopCartDataProvider(CartDataProvider):

    def acquire_event(self, context):
        while not IBuyableEvent.providedBy(context):
            context = aq_parent(context)
        return context

    def validate_count(self, uid, count):
        """Validate setting cart item count for uid.

        uid - Is the cart item UID.
        count - If count is 0, it means that a cart item is going to be
        deleted, which is always allowed. If count is > 0, it's the aggregated
        item count in cart.
        """
        count = float(count)
        # count is 0, return
        if not count:
            return {'success': True, 'error': ''}
        cart_item = get_object_by_uid(self.context, uid)
        item_data = get_item_data_provider(cart_item)
        buyable_event = self.acquire_event(cart_item)
        buyable_event_data = IBuyableEventData(buyable_event)
        # cart count limit is set for all event tickets
        if buyable_event_data.cart_count_limit:
            related_uids = IEventTickets(cart_item).related_uids
            aggregated_count = count
            items = extractitems(readcookie(self.request))
            for ticket_uid in related_uids:
                # we already have count for item to validate
                if uid == ticket_uid:
                    continue
                aggregated_count += float(
                    aggregate_cart_item_count(ticket_uid, items))
            if aggregated_count > buyable_event_data.cart_count_limit:
                message = translate(
                    _('event_tickets_limit_reached',
                      default="Limit of tickets for this event reached"),
                    context=self.request)
                return {'success': False, 'error': message}
        # cart count limit is set for ticket
        elif item_data.cart_count_limit:
            if count > item_data.cart_count_limit:
                message = translate(
                    _('ticket_limit_reached',
                      default="Limit for this ticket reached"),
                    context=self.request)
                return {'success': False, 'error': message}
        # stock check
        item_state = get_item_state(cart_item, self.request)
        if item_state.validate_count(count):
            return {'success': True, 'error': ''}
        # out of stock
        message = translate(_('trying_to_add_more_tickets_than_available',
                              default="Not enough tickets available, abort."),
                            context=self.request)
        return {'success': False, 'error': message}


@implementer(ICartItemDataProvider)
@adapter(ITicketOccurrence)
class TicketOccurrenceCartItemDataProvider(object):

    def __init__(self, context):
        # Have to set this on object, otherwise they are masqued by __getattr__
        object.__setattr__(self, 'context', context)
        parent_context = ICartItemDataProvider(aq_parent(context))
        object.__setattr__(self, 'parent_context', parent_context)
        own_attr = ['title', ]
        object.__setattr__(self, 'own_attr', own_attr)

    @property
    def title(self):
        return ticket_title_generator(self.context)['title']

    def __getattr__(self, name):
        if name in self.own_attr:
            return getattr(self.context, name)
        else:
            return getattr(self.parent_context, name)


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

    @property
    def some_reservations_alert(self):
        message = bps_(u'alert_item_some_reserved',
                       default=u'Partly reserved')
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
            # XXX: cart item state needs love how to display item
            #      warnings
            return self.some_reservations_alert
            # return self.number_reservations_alert(reserved)
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


@implementer(ISharedData)
class SharedData(EventTicketsBase):

    @property
    def shared_data_key(self):
        raise NotImplementedError(u"Abstract ``SharedData`` does not "
                                  u"implement ``shared_data_key``")

    @property
    def shared_data_context(self):
        raise NotImplementedError(u"Abstract ``SharedData`` does not "
                                  u"implement ``shared_data_context``")

    @property
    def shared_data(self):
        annotations = IAnnotations(self.shared_data_context, None)
        if annotations is None:
            # return dummy dict, prevents add form from raising an error
            return dict()
        data = annotations \
            and annotations.get(self.shared_data_key, None) \
            or None
        if data is None:
            data = OOBTree()
            annotations[self.shared_data_key] = data
        return data

    def get(self, field_name):
        return self.shared_data.get(self.related_key, {}).get(field_name)

    def set(self, field_name, value):
        shared_data = self.shared_data
        data = shared_data.setdefault(self.related_key, PersistentDict())
        if value is None:
            data[field_name] = None
        else:
            data[field_name] = float(value)


SHARED_STOCK_DATA_KEY = 'bda.plone.ticketshop.shared_stock'


@implementer(ISharedStockData)
class SharedStockData(SharedData):

    @property
    def shared_data_key(self):
        return SHARED_STOCK_DATA_KEY


@adapter(ITicket)
class TicketSharedStock(EventTickets, SharedStockData):

    @property
    def shared_data_context(self):
        return aq_parent(self.context)


@adapter(ITicketOccurrence)
class TicketOccurrenceSharedStock(EventTicketOccurrences, SharedStockData):

    @property
    def shared_data_context(self):
        return aq_parent(aq_parent(self.context))


SHARED_BUYABLE_PERIOD_DATA_KEY = 'bda.plone.ticketshop.shared_buyable_period'


@implementer(ISharedBuyablePeriodData)
class SharedBuyablePeriodData(SharedData):

    @property
    def shared_data_key(self):
        return SHARED_BUYABLE_PERIOD_DATA_KEY


@adapter(ITicket)
class TicketSharedBuyablePeriod(EventTickets, SharedBuyablePeriodData):

    @property
    def shared_data_context(self):
        return aq_parent(self.context)


@adapter(ITicketOccurrence)
class TicketOccurrenceSharedBuyablePeriod(EventTicketOccurrences,
                                          SharedBuyablePeriodData):

    @property
    def shared_data_context(self):
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

    def create_booking(self, order, cart_data, uid, count, comment):
        booking = super(TicketOrderCheckoutAdapter, self).create_booking(
            order, cart_data, uid, count, comment
        )

        brain = get_catalog_brain(self.context, uid)
        if not brain:
            return
        buyable = brain.getObject()
        titledict = ticket_title_generator(buyable)

        booking.attrs['title'] = titledict['title']
        if titledict['eventtitle']:
            booking.attrs['eventtitle'] = titledict['eventtitle']
        if titledict['eventstart']:
            booking.attrs['eventstart'] = titledict['eventstart']
        if titledict['eventend']:
            booking.attrs['eventend'] = titledict['eventend']
        return booking
