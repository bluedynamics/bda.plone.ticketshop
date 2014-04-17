====================
bda.plone.ticketshop
====================

Shop for selling Tickets to Events based on ``plone.app.event`` and
``bda.plone.shop``.

TODO
====

- TicketOccurrence proxies it's properties from it's parent, the Ticket. but it
  implements IBuyable and thus it gets extended by the BuyableExtender, etc.
  We have to make sure, none of these attributes are used or remove the
  IBuyable interface.


Userstory
=========

* An ``Event`` gets created with or without recurrence rule.

* Inside this Event one or more ``Ticket`` objects are created. For each event
  occurrence a ``TicketOccurrence`` gets created inside the ticket object.

* If event view shows the main event, main ticket objects are available to
  buy.

* If event view shows an occurrence of the event, the corresponding
  ticket occurrence objects are available to buy.

* If event recurrence rule is changed, ticket occurrences keep untouched.
  A re-mapping of the ticket ocurrence to an event occurrence must happen
  manually if desired by setting the corresponding start and end dates.


Content Structure
=================

* Buyable Event (Recurring Event)
    * Ticket (Buyable)
        * Ticket Occurrence (Buyable)
            - Ticket occurrence information equates event occurrence
              information
