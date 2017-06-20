# -*- coding: utf-8 -*-
from bda.plone.ticketshop.common import ticket_title_generator
from bda.plone.ticketshop.interfaces import ITicket
from plone.indexer.decorator import indexer


@indexer(ITicket)
def ticket_title_indexer(obj):
    return ticket_title_generator(obj)['title']
