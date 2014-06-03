Changelog
=========


1.0dev
------

- Fix link to booking in ``@@myorder`` view, like in ``@@order`` view and
  protect the ``@@myorder`` view with ``bda.plone.orders.ViewOwnOrders``.
  [thet]

- Add ITrading based extender and DataProvider for ITickets, providing no
  fields and returning None to exclude the trading feature.
  [thet]

- Also register ItemNotificationTextExtender also for IBuyableEvent, making
  these fields available on the event itself.
  [thet]

- Add TicketOccurrenceShippingExtender alongside
  TicketOccurrenceBuyableExtender, which returns an empty field list to hide
  shipping and buyable fields from ITicketOccurrence objects. Add a
  IShippingItem data provider for ITicket objects, returning 0 for weight and
  the default value for shipping_item_shippable.
  [thet, rnix]

- Add event subscriber for Ticket, which listens on worflow state changes. The
  subscriber applies the workflow transition of the Ticket to any contained
  Ticket Occurrences, if possible.
  [thet]

- initial work.
  [rnix, thet]
