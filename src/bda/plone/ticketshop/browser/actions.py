from zExceptions import Redirect
from Products.Five import BrowserView
from ..interfaces import (
    IBuyableEvent,
    ITicketOccurrenceData,
)


class TicketOccurrence(BrowserView):

    def display(self):
        return IBuyableEvent.providedBy(self.context)

    def create(self):
        ITicketOccurrenceData(self.context).create_ticket_occurrences()
        raise Redirect(self.context.absolute_url())
