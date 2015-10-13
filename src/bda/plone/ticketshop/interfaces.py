from bda.plone.shop.interfaces import IShopExtensionLayer
from zope.interface import Attribute
from zope.interface import Interface


class ITicketShopExtensionLayer(IShopExtensionLayer):
    """Browser layer for bda.plone.ticketshop
    """


class IBuyableEvent(Interface):
    """Marker interfaces for buyable events.
    """


class ISharedStock(Interface):
    """Marker for items providing shared stock.
    """


class ISharedBuyablePeriod(Interface):
    """Marker for items providing shared buyable period.
    """


class ITicket(ISharedStock, ISharedBuyablePeriod):
    """Marker interfaces for ticket.
    """


class ITicketOccurrence(ITicket):
    """Marker interfaces for ticket occurrence.
    """


class IBuyableEventData(Interface):
    """Provide information relevant for being buyable event.
    """

    cart_count_limit = Attribute(u"Max count of tickets of this event in cart")


class IEventTickets(Interface):
    """Interface for providing ticket related information.
    """

    related_key = Attribute(u"Related tickets key.")

    related_uids = Attribute(u"List of uids of related tickets.")


class ISharedData(IEventTickets):
    """Interface for accessing shared data.
    """

    shared_data_key = Attribute(u"Annotation key for shared data.")

    shared_data_context = Attribute(u"Context which holds shared data.")

    def get(field_name):
        """Get shared data value for field name.
        """

    def set(field_name, value):
        """Set shared data value for field name.
        """


class ISharedStockData(ISharedData):
    """Interface for accessing shared stock data.
    """


class ISharedBuyablePeriodData(ISharedData):
    """Interface for accessing shared buyable period data.
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
