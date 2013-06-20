from zExceptions import Redirect
from Products.Five import BrowserView
from ..interfaces import IBuyableEvent


class TicketOccurrence(BrowserView):

    def display(self):
        return IBuyableEvent.providedBy(self.context)

    def create(self):
        print 'create ticket occurrences'
        raise Redirect(self.context.absolute_url())
