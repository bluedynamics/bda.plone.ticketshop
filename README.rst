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


Running tests
-------------

If you have run the buildout, you can run all tests like so::

    ./bin/test -s bda.plone.ticketshop

The -t switch allows you to run a specific test file or method. The
``--list-tests`` lists all available tests.

To run the robot tests do::

    ./bin/test --all -s bda.plone.ticketshop -t robot

For development, it might be more convenient to start a test server and run
robot tests individually, like so (-d to start Zope in DEBUG-MODE)::

    ./bin/robot-server bda.plone.ticketshop.tests.TicketshopAT_ROBOT_TESTING -d
    ./bin/robot src/bda/plone/ticketshop/tests/robot/test_shop_orderprocess.robot 

To automatically land in the debug shell on test-failure, use::
    
    ./bin/robot-debug src/bda/plone/shop/tests/robot/test_shop_orderprocess.robot
