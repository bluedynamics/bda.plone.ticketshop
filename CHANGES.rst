Changelog
=========

1.0 (unreleased)
----------------

- Make the ``ticket_title_generator`` more robust against cases, where a corresponding event occurrence of a ticket occurence isn't available anymore.
  [thet]

- Add ``item_stock_warning_threshold``, like in ``bda.plone.shop.at.SharedStockExtender``.
  Refs: https://github.com/bluedynamics/bda.plone.shop/pull/63 
  [thet]

- Use ``bda.plone.orders.mailnotify.BOOKING_CANCELLED_TITLE_ATTRIBUTE``
  to set ``eventtitle`` as booking cancelled notification title.
  [rnix]

- Configure Ticket and TicketOccurrence to use the ``plone.content.itemView``
  caching rule, if z3c.caching is available.
  [thet]

- Don't cache _tickets on the request. This doesn't work, if the buyable
  viewlet is shown multiple times on one page, e.g. for event_listing.
  [thet]

- Don't let the buyable_availability view break, if there are no tickets
  available.
  [thet]

- Make buyable_availability view for display in event_listing.
  [bennyboy, thet]

- Ticketshop support for Dexterity based events. Tickets and TicketOccurrences
  are still Archetype objects, though.
  [thet]

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
