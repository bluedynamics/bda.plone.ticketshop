from zope.interface import Interface


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
