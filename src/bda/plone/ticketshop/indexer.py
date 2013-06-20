from plone.indexer import indexer
from .interfaces import ITicketOccurrence


@indexer(ITicketOccurrence)
def ticket_occurrence_start(obj):
    return obj.getStartDate()


# XXX: needed?
@indexer(ITicketOccurrence)
def ticket_occurrence_end(obj):
    return obj.getEndDate()
