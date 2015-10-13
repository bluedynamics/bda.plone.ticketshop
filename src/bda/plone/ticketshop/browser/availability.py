# -*- coding: utf-8 -*-
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.cart import extractitems
from bda.plone.cart import get_item_state
from bda.plone.cart import readcookie
from bda.plone.shop.browser.availability import CartItemAvailability
from bda.plone.shop.interfaces import IBuyablePeriod
from bda.plone.ticketshop.interfaces import ISharedStock
from bda.plone.ticketshop.interfaces import ISharedStockData
from zope.component import adapter
from zope.component import queryAdapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest

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
    def full_available_message(self):
        available = self.available
        if available is None:
            available = ''
        else:
            available = int(available)
        message = _(u'ticket_full_available_message',
                    default=u'${available} tickets(s) available.',
                    mapping={'available': available})
        return message

    @property
    def critical_available_message(self):
        message = _(u'ticket_critical_available_message',
                    default=u'Just ${available} tickets(s) left.',
                    mapping={'available': int(self.available)})
        return message

    @property
    def overbook_available_message(self):
        state = get_item_state(self.context, self.request)
        overbook = self.stock.overbook
        if overbook is None:
            reservable = ''
        else:
            reservable = int(overbook - state.reserved)
        message = _(u'ticket_overbook_available_message',
                    default=u'Tickets are sold out. You can add ${reservable} '
                            u'tickets on a reservations list. If some tickets '
                            u'gets refused, you\'ll get informed.',
                    mapping={'reservable': reservable})
        return message

    @property
    def purchasable_until_message(self):
        date = ulocalized_time(
            queryAdapter(self.context, IBuyablePeriod).expires,
            long_format=1,
            context=self.context,
            request=self.request,
        )
        message = _(u'ticket_purchasable_until_message',
                    default=u'Tickets are purchasable until ${date}',
                    mapping={'date': date})
        return message

    @property
    def purchasable_as_of_message(self):
        date = ulocalized_time(
            queryAdapter(self.context, IBuyablePeriod).effective,
            long_format=1,
            context=self.context,
            request=self.request,
        )
        message = _(u'ticket_purchasable_as_of_message',
                    default=u'Tickets are purchasable as of ${date}',
                    mapping={'date': date})
        return message
