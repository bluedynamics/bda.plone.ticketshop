# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from bda.plone.ticketshop.interfaces import IBuyableEvent
from bda.plone.ticketshop.interfaces import ITicketOccurrenceData


class TicketOccurrence(BrowserView):

    def display(self):
        return IBuyableEvent.providedBy(self.context)

    def create(self):
        ITicketOccurrenceData(self.context).create_ticket_occurrences()
        self.request.response.redirect(self.context.absolute_url())
