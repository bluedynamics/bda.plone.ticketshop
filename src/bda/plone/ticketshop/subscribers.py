from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from bda.plone.ticketshop import messageFactory as _
from bda.plone.ticketshop.interfaces import ITicket
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from zope.component import adapter
from zope.globalrequest import getRequest


@adapter(ITicket, IActionSucceededEvent)
def ticket_wf_changed(obj, event):
    if ITicketOccurrence.providedBy(obj):
        # Don't change state for subobjects of TicketOccurrence and avoid
        # infinite loops. We land in here after changing the state for
        # TicketOccurrence objects.
        return
    wft = getToolByName(obj, 'portal_workflow')
    changed = []
    failed = []
    for sub in obj.contentValues():
        if not ITicketOccurrence.providedBy(sub):
            # WTF? continue.
            continue
        try:
            wft.doActionFor(sub, event.action)
            changed.append(sub)
        except WorkflowException:
            failed.append(sub)

    state = wft.getInfoFor(obj, 'review_state')
    if changed:
        msg = _(
            'msg_changed_ticketoccurrence_workflow',
            default=u"Set the workflow to ${state} for these "
                    u"Ticket Occurrences: ${items}.",
            mapping={
                'state': state,
                'items': ', '.join([it.id for it in changed])
            }

        )
        IStatusMessage(getRequest()).addStatusMessage(msg, 'info')

    if failed:
        msg = _(
            'msg_failed_ticketoccurrence_workflow',
            default=u"Failed to set the workflow to ${state} for these "
                    u"Ticket Occurrences: ${items}.",
            mapping={
                'state': state,
                'items': ', '.join([
                    '{} ({})'.format(it.id, wft.getInfoFor(it, 'review_state'))
                    for it in failed])
            }

        )
        IStatusMessage(getRequest()).addStatusMessage(msg, 'warning')
