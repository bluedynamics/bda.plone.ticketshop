from zope.interface import implementer
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from plone.app.event.base import DT
from plone.formwidget.datetime.at import DatetimeWidget
from bda.plone.shop.interfaces import IBuyable
from ..interfaces import ITicketOccurrence
from ..config import PROJECTNAME
from .. import _


schema = atapi.Schema((

    atapi.DateTimeField('startDate',
        required=True,
        searchable=False,
        accessor='start',
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_start', default=u'Start'),
            description=_(u'help_start',
                          default=u"Date and Time"),
            ),
        ),

    atapi.DateTimeField('endDate',
        required=True,
        searchable=False,
        accessor='end',
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_end', default=u'End'),
            description=_(u'help_end',
                          default=u"Date and Time"),
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

    security.declareProtected('View', 'start')
    def start(self):
        return self.getStartDate()

    security.declareProtected('View', 'end')
    def end(self):
        return self.getEndDate()

atapi.registerType(TicketOccurrence, PROJECTNAME)
