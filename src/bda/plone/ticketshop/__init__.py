from bda.plone.orders import mailnotify
from bda.plone.ticketshop import permissions  # nopep8
from zope.i18nmessageid import MessageFactory


messageFactory = MessageFactory('bda.plone.ticketshop')  # nopep8

mailnotify.BOOKING_CANCELLED_TITLE_ATTRIBUTE = 'eventtitle'
