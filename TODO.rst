TODO
====

- DX support, pt 1:

  <adapter
    name="bda.plone.ticketshop.event"
    factory=".BuyableEventExtender"
    provides="archetypes.schemaextender.interfaces.IOrderableSchemaExtender" />
  <adapter
    for="bda.plone.ticketshop.interfaces.IBuyableEvent"
    factory=".ATSharedBuyablePeriod" />

  <adapter
    name="bda.plone.shop.itemnotificationtext"
    for="bda.plone.ticketshop.interfaces.IBuyableEvent"
    factory="bda.plone.shop.at.ItemNotificationTextExtender"
    provides="archetypes.schemaextender.interfaces.IOrderableSchemaExtender" />

- Buyable and shipping schema extender overwrites for Ticketoccurrence should
  be removed. The schema extenders should instead better be registered for more
  specific interfaces.

- Test for correct proxying of IBuyable data provider properties for
  TicketOccurrence.

- Test for commit b3f18a0da2004529d1a48f670842382649d8f57e "allow setting
  of value 0" 
