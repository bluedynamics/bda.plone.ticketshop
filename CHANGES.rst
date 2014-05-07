Changelog
=========


1.0dev
------

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
