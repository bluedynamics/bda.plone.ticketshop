# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_parent
from Products.Five import BrowserView
from bda.plone.cart import get_item_availability
from bda.plone.shop import permissions
from bda.plone.shop.browser.buyable import BuyableControls as _BuyableControls
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData
from plone.uuid.interfaces import IUUID


class BuyableControls(_BuyableControls):

    @property
    def show_available(self):
        return False


class SharedStockBuyables(BrowserView):

    @property
    def _item_availability(self):
        ret = None
        if self.tickets:
            # tickets might be empty
            ret = get_item_availability(self.tickets[0], self.request)
        else:
            # Dummy object
            ret = type('obj', (object,), {
                'display': False,
                'signal': 'red',
                'details': ''
            })
        return ret

    @property
    def can_view_buyable_info(self):
        sm = getSecurityManager()
        return sm.checkPermission(permissions.ViewBuyableInfo, self.context)

    @property
    def listen_uid_css(self):
        classes = list()
        for ticket in self.tickets:
            classes.append('cart_item_%s' % IUUID(ticket))
        return ' '.join(classes)

    @property
    def show_available(self):
        return self._item_availability.display

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
        data = ITicketOccurrenceData(self.context)
        return data.tickets


class BuyableEventOccurrenceTickets(SharedStockBuyables):

    @property
    def ticket_context(self):
        return aq_parent(self.context)

    @property
    def tickets(self):
        occurrence_id = self.context.id
        data = ITicketOccurrenceData(aq_parent(self.context))
        return data.ticket_occurrences(occurrence_id)
