Changelog
=========

1.0 (unreleased)
----------------

- Buyable period is shared among tickets now.
  [rnix]

- Adopt custom availability details to consider buyable period.
  [rnix]

- Return "Partly reserved" message in cart item state.
  [rnix]

- Add the URL to the event or event occurrence for a ticket or ticket
  occurrence in CSV exports.
  [thet]

- Remove booking url customizations. We now link to the ticket and not to the
  event, which is the default behavior from bda.plone.orders. The ticket itself
  links to the event.
  [thet]

- Instead of ``plone.app.uuid.utils.uuidToObject`` use
  ``bda.plone.cart.get_object_by_uid``, which does the same but can handle
  ``uuid.UUID`` and string objects.
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
