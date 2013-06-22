from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.cart import (
    extractitems,
    readcookie,
    get_item_state,
)
from bda.plone.shop.browser.availability import CartItemAvailability
from ..interfaces import (
    ISharedStock,
    ISharedStockData,
)


_ = MessageFactory('bda.plone.ticketshop')


@adapter(ISharedStock, IBrowserRequest)
class SharedCartItemAvailability(CartItemAvailability):
    details_template = ViewPageTemplateFile('availability_details.pt')

    @property
    def available(self):
        available = self.stock.available
        shared_stock_data = ISharedStockData(self.context)
        related_uids = shared_stock_data.related_uids
        if available is not None:
            cart_items = extractitems(readcookie(self.request))
            for item_uid in related_uids:
                for uid, count, comment in cart_items:
                    if uid == item_uid:
                        available -= float(count)
        return available

    @property
    def ticket_full_available_message(self):
        message = _(u'ticket_full_available_message',
                    default=u'${available} tickets(s) available.',
                    mapping={'available': int(self.available)})
        return message

    @property
    def ticket_critical_available_message(self):
        message = _(u'ticket_critical_available_message',
                    default=u'Just ${available} tickets(s) left.',
                    mapping={'available': int(self.available)})
        return message

    @property
    def ticket_overbook_available_message(self):
        state = get_item_state(self.context, self.request)
        reservable = self.stock.overbook - state.reserved
        message = _(u'ticket_overbook_available_message',
                    default=u'Tickets are sold out. You can add ${reservable} '
                            u'tickets on a reservations list. If some tickets '
                            u'gets refused, you\'ll get informed.',
                    mapping={'reservable': int(reservable)})
        return message
