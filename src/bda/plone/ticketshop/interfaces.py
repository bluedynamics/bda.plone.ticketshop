from zope.interface import Interface
from zope.interface import Attribute
from bda.plone.shop.interfaces import IShopExtensionLayer


class ITicketShopExtensionLayer(IShopExtensionLayer):
    """Browser layer for bda.plone.ticketshop
    """


class IBuyableEvent(Interface):
    """Marker interfaces for buyable events.
    """


class ISharedStock(Interface):
    """Marker for items providing shared stock.
    """


class ITicket(ISharedStock):
    """Marker interfaces for ticket.
    """


class ITicketOccurrence(ISharedStock):
    """Marker interfaces for ticket occurrence.
    """


class ISharedStockData(Interface):
    """Interface for accessing shared stock data.
    """

    shared_stock_context = Attribute(u"Context which holds shared stock data.")

    shared_stock_key = Attribute(u"Shared stock key.")

    related_uids = Attribute(u"List of uids sharing stock data related to "
                             u"adapted context.")

    def get(field_name):
        """Get shared stock value for field name.
        """

    def set(field_name, value):
        """Set shared stock value for field name.
        """


class ITicketOccurrenceData(Interface):
    """Buyable event adapter interface for accessing and managing ticket
    occurrences.
    """

    tickets = Attribute(u"Ticket objects contained in event")

    def ticket_occurrences(occurrence_id):
        """Return Ticket Occurrence objects for occurrence_id.
        """

    def create_ticket_occurrences():
        """Create Ticket occurrence objects inside all ticket objects for
        event occurrences if not exists yet.
        """
