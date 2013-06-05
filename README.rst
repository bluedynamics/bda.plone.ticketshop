====================
bda.plone.ticketshop
====================

Shop for selling Tickets to Events based on ``plone.app.event`` and
``bda.plone.shop``.


Userstory
=========

* An ``Event`` gets created with or without recurrence rule.

* Inside this Event one or more ``Ticket`` objects are created. For each event
  ocurrence a ``TicketOccurence`` gets created inside the ticket object.

* If event view shows the main event, main ticket objects are available to
  buy.

* If event view shows an occurence of the event, the corresponding
  ticket occurence objects are available to buy.

* If event recurrence rule is changed, ticket occurences keep untouched.
  A re-mapping of the ticket ocurrence to an event occurence must happen
  manually if desired by setting the corresponding start and end dates.


Content Structure
=================

* FolderishEventType(RecurringEvent)
    * Ticket(Buyable)
        * OccuringTicket(Buyable)
            - Ticket occuring information equates event occurence information
