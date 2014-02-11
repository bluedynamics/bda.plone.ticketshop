from Products.CMFCore.permissions import setDefaultRoles


PROJECTNAME = "bda.plone.ticketshop"


ADD_PERMISSIONS = {
    "BuyableEvent": "bda.plone.ticketshop: Add Buyable Event",
    "Ticket": "bda.plone.ticketshop: Add Ticket",
    "TicketOccurrence": "bda.plone.ticketshop: Add Ticket Occurrence",
}


setDefaultRoles(ADD_PERMISSIONS['BuyableEvent'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
setDefaultRoles(ADD_PERMISSIONS['Ticket'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
setDefaultRoles(ADD_PERMISSIONS['TicketOccurrence'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
