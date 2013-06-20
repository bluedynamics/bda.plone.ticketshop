from zope.interface import (
    Interface,
    Attribute,
)


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

    def get():
        """Get shared stock value.
        """

    def set(value):
        """Set shared stock value.
        """


class ITicketOccurrenceData(Interface):
    """Buyable event adapter interface for accessing and managing ticket
    occurrences.
    """

    tickets = Attribute(u"Ticket objects contained in event")

    def create_ticket_occurrences():
        """Create Ticket occurrence objects inside all ticket objects for
        event occurrences if not exists yet.
        """
