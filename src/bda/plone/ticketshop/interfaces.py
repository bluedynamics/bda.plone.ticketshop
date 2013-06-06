from zope.interface import Interface


class IBuyableEvent(Interface):
    """Marker interfaces for buyable events.
    """


class ITicket(Interface):
    """Marker interfaces for ticket.
    """


class ITicketOccurrence(Interface):
    """Marker interfaces for ticket occurrence.
    """
