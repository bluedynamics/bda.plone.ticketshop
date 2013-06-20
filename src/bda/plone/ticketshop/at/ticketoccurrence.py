from .. import _
from ..config import PROJECTNAME
from ..interfaces import ITicketOccurrence
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bda.plone.shop.interfaces import IBuyable
from plone.event.utils import pydt
from plone.formwidget.datetime.at import DatetimeWidget
from zope.interface import implementer


schema = atapi.Schema((

    atapi.DateTimeField('startDate',
        required=True,
        searchable=False,
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_start', default=u'Start'),
            description=_(u'help_start',
                          default=u"Occurence Start Date"),
            ),
        ),

    atapi.DateTimeField('endDate',
        required=True,
        searchable=False,
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_end', default=u'End'),
            description=_(u'help_end',
                          default=u"Occurence End Date"),
            ),
        ),
))


TicketOccurrence_schema = atapi.BaseSchema.copy() + schema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseContent, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    portal_type = 'Ticket Occurrence'
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True

    security.declareProtected('View', 'start_date_iso')
    def start_date_iso(self):
        return pydt(self.getStartDate(), exact=False).date().isoformat()

    security.declareProtected('View', 'end_date_iso')
    def end_date_iso(self):
        return pydt(self.getEndDate(), exact=False).date().isoformat()

atapi.registerType(TicketOccurrence, PROJECTNAME)
