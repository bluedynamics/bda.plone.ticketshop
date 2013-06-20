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
            with_time=1,
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
            with_time=1,
            ),
        ),
))


TicketOccurrence_schema = atapi.BaseFolderSchema.copy() + schema.copy()


@implementer(ITicketOccurrence, IBuyable)
class TicketOccurrence(atapi.BaseFolder, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    portal_type = 'Ticket Occurrence'
    meta_type = 'TicketOccurrence'
    _at_rename_after_creation = True
    schema = TicketOccurrence_schema
    exclude_from_nav = True

    def _dt_getter(self, field):
        event = aq_parent(aq_parent(self))
        timezone = event.getField('timezone').get(event)
        dt = self.getField(field).get(self)
        return dt.toZone(timezone)

    def _dt_setter(self, fieldtoset, value, **kwargs):
        if not isinstance(value, DateTime):
            value = DT(value)
        value = DateTime(
            '%04d-%02d-%02dT%02d:%02d:%02d' % (
                value.year(),
                value.month(),
                value.day(),
                value.hour(),
                value.minute(),
                int(value.second())
            )
        )
        self.getField(fieldtoset).set(self, value, **kwargs)

    security.declareProtected('View', 'start')
    def start(self):
        return self._dt_getter('startDate')

    security.declareProtected('View', 'end')
    def end(self):
        return self._dt_getter('endDate')

    security.declareProtected(ModifyPortalContent, 'setStartDate')
    def setStartDate(self, value, **kwargs):
        self._dt_setter('startDate', value, **kwargs)

    security.declareProtected(ModifyPortalContent, 'setEndDate')
    def setEndDate(self, value, **kwargs):
        self._dt_setter('endDate', value, **kwargs)


atapi.registerType(TicketOccurrence, PROJECTNAME)
