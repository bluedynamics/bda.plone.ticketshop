from Products.CMFCore.permissions import setDefaultRoles


ADD_PERMISSIONS = {
    "Buyable Event": "bda.plone.ticketshop: Add Buyable Event",
    "Ticket": "bda.plone.ticketshop: Add Ticket",
    "Ticket Occurrence": "bda.plone.ticketshop: Add Ticket Occurrence",
}


setDefaultRoles(ADD_PERMISSIONS['Buyable Event'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
setDefaultRoles(ADD_PERMISSIONS['Ticket'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
setDefaultRoles(ADD_PERMISSIONS['Ticket Occurrence'], (
    'Contributor', 'Manager', 'Owner', 'Site Administrator'))
