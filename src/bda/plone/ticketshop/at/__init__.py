from DateTime import DateTime
from DateTime.DateTime import safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IFieldDefaultProvider
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import FloatField
from Products.CMFCore import utils
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bda.plone.orders.interfaces import ITrading
from bda.plone.shipping.interfaces import IShippingItem
from bda.plone.shop.at import ATCartItemDataProvider
from bda.plone.shop.interfaces import IBuyablePeriod
from bda.plone.ticketshop import messageFactory as _
from bda.plone.ticketshop import permissions
from bda.plone.ticketshop.common import ticket_title_generator
from bda.plone.ticketshop.interfaces import IBuyableEvent
from bda.plone.ticketshop.interfaces import IBuyableEventData
from bda.plone.ticketshop.interfaces import ISharedBuyablePeriod
from bda.plone.ticketshop.interfaces import ISharedBuyablePeriodData
from bda.plone.ticketshop.interfaces import ISharedStock
from bda.plone.ticketshop.interfaces import ISharedStockData
from bda.plone.ticketshop.interfaces import ITicket
from bda.plone.ticketshop.interfaces import ITicketOccurrence
from bda.plone.ticketshop.interfaces import ITicketShopExtensionLayer
from datetime import datetime
from zope.component import adapter
from zope.component import queryAdapter
from zope.interface import implementer


PROJECTNAME = "bda.plone.ticketshop.at"


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    from bda.plone.ticketshop.at import buyableevent  # nopep8
    from bda.plone.ticketshop.at import ticket  # nopep8
    from bda.plone.ticketshop.at import ticketoccurrence  # nopep8
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME), PROJECTNAME)
    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit(
            "%s: %s" % (PROJECTNAME, atype.meta_type),
            content_types=(atype,),
            permission=permissions.ADD_PERMISSIONS[atype.meta_type],
            extra_constructors=(constructor,),
        ).initialize(context)


def field_value(obj, field_name):
    try:
        acc = obj.getField(field_name).getAccessor(obj)
        return acc()
    except (KeyError, TypeError):
        raise AttributeError


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class ExtenderBase(object):

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        return original


class XFloatField(ExtensionField, FloatField):
    pass


@adapter(IBuyableEvent)
class BuyableEventExtender(ExtenderBase):
    layer = ITicketShopExtensionLayer
    fields = [
        XFloatField(
            name='item_cart_count_limit',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_item_cart_count_limit',
                        default=u'Max count of this item in cart'),
            ),
        ),
    ]


@implementer(IBuyableEventData)
@adapter(IBuyableEvent)
class ATBuyableEventData(object):
    """Accessor Interface
    """

    def __init__(self, context):
        self.context = context

    @property
    def cart_count_limit(self):
        return field_value(self.context, 'item_cart_count_limit')


class ATTicketCartItemDataProvider(ATCartItemDataProvider):
    """Custom CartItemDataProvider for Archetypes Tickets, providing a custom
    title.
    """

    @property
    def title(self):
        return ticket_title_generator(self.context)['title']


# Overwrite schema extenders for ITicket and/or ITicketOccurrence to not
# display fields not intendent to be changed on these objects

# TODO: these overwrites should better go away. The schema extenders should
# instead better be registered for more specific interfaces.

@adapter(ITicket)
class TicketTradingExtender(ExtenderBase):
    """Overwrite default trading for tickets providing no fields.
    """
    layer = ITicketShopExtensionLayer
    fields = []


@implementer(ITrading)
@adapter(ITicket)
class TicketTrading(object):
    """Custom Accessor Interface
    """

    def __init__(self, context):
        self.context = context
        self.item_number = None
        self.gtin = None


@adapter(ITicketOccurrence)
class TicketOccurenceBuyableExtender(ExtenderBase):
    """Overwrite default buyable extender for ticket occurrences providing no
    fields.
    """
    layer = ITicketShopExtensionLayer
    fields = []


@adapter(ITicketOccurrence)
class TicketOccurenceShippingExtender(ExtenderBase):
    """Overwrite default shipping extender for ticket occurrences providing no
    fields.
    """
    layer = ITicketShopExtensionLayer
    fields = []


@implementer(IShippingItem)
@adapter(ITicket)
class TicketShippingItem(object):
    """Custom IShippingItem data provider, returning 0 for weight and the
    default shippable setting from the control panel.
    """

    def __init__(self, context):
        self.context = context

    @property
    def shippable(self):
        return queryAdapter(
            self.context,
            IFieldDefaultProvider,
            'shipping_item_shippable',
            default=lambda: False)()

    @property
    def weight(self):
        return 0


@implementer(IExtensionField)
class SharedDataExtensionField(object):

    @property
    def data_accessor_interface(self):
        raise NotImplementedError(u"Abstract ``SharedDataExtensionField`` "
                                  u"does not implement "
                                  u"``data_accessor_interface``")

    def get(self, instance, **kwargs):
        __traceback_info__ = (self.getName(), instance, kwargs)
        return self.data_accessor_interface(instance).get(self.getName())

    def getRaw(self, instance, **kwargs):
        return self.get(instance, **kwargs)

    def set(self, instance, value, **kwargs):
        __traceback_info__ = (self.getName(), instance, value, kwargs)
        self.data_accessor_interface(instance).set(self.getName(), value)

    def getAccessor(self, instance):
        def accessor(**kw):
            return self.get(instance, **kw)
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor(**kw):
            return self.getRaw(instance, **kw)
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            self.set(instance, value, **kw)
        return mutator

    def getIndexAccessor(self, instance):
        name = getattr(self, 'index_method', None)
        if name is None or name == '_at_accessor':
            return self.getAccessor(instance)
        elif name == '_at_edit_accessor':
            return self.getEditAccessor(instance)
        elif not isinstance(name, basestring):
            raise ValueError('Bad index accessor value: %r', name)
        else:
            return getattr(instance, name)


class SharedStockExtensionField(SharedDataExtensionField):

    @property
    def data_accessor_interface(self):
        return ISharedStockData


class XSharedStockFloatField(SharedStockExtensionField, FloatField):

    def set(self, instance, value, **kwargs):
        if value == '':
            value = None
        elif value is not None:
            __traceback_info__ = (self.getName(), instance, value, kwargs)
            if isinstance(value, basestring):
                value = value.replace(',', '.')
            value = float(value)
        super(XSharedStockFloatField, self).set(instance, value, **kwargs)


class XSharedStockBooleanField(SharedStockExtensionField, BooleanField):

    def get(self, instance, **kwargs):
        val = super(XSharedStockBooleanField, self).get(instance, **kwargs)
        return bool(val)

    def getRaw(self, instance, **kwargs):
        val = super(XSharedStockBooleanField, self).getRaw(instance, **kwargs)
        return bool(val)

    def set(self, instance, value, **kwargs):
        if not value or value == '0' or value == 'False':
            value = False
        else:
            value = True
        super(XSharedStockBooleanField, self).set(instance, value, **kwargs)


@implementer(IFieldDefaultProvider)
@adapter(ISharedStock)
def default_item_display_stock(context):
    # XXX: field default provider gets called but value is ignored.
    return lambda: True


@adapter(ISharedStock)
class SharedStockExtender(ExtenderBase):
    layer = ITicketShopExtensionLayer
    fields = [
        XSharedStockBooleanField(
            name='item_display_stock',
            schemata='Shop',
            widget=BooleanField._properties['widget'](
                label=_(u'label_item_display_stock', u'Display item stock'),
            ),
        ),
        XSharedStockFloatField(
            name='item_available',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_item_available', u'Item stock available'),
            ),
        ),
        XSharedStockFloatField(
            name='item_overbook',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_item_overbook', u'Item stock overbook'),
            ),
        ),
        XFloatField(
            name='item_stock_warning_threshold',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_stock_warning_threshold',
                        default=u'Item stock warning threshold.'),
            ),
        ),
    ]


class SharedBuyablePeriodExtensionField(SharedDataExtensionField):

    @property
    def data_accessor_interface(self):
        return ISharedBuyablePeriodData


class XSharedBuyablePeriodDateTimeField(SharedBuyablePeriodExtensionField,
                                        atapi.DateTimeField):

    def set(self, instance, value, **kwargs):
        if not value:
            value = None
        elif not isinstance(value, DateTime):
            try:
                value = DateTime(value)
                if value.timezoneNaive():
                    zone = value.localZone(safelocaltime(value.timeTime()))
                    parts = value.parts()[:-1] + (zone,)
                    value = DateTime(*parts)
            except DateTimeError:
                value = None
        super(XSharedBuyablePeriodDateTimeField, self).set(
            instance, value, **kwargs)


@adapter(ISharedBuyablePeriod)
class SharedBuyablePeriodExtender(ExtenderBase):
    layer = ITicketShopExtensionLayer

    fields = [
        XSharedBuyablePeriodDateTimeField(
            name='buyable_effective',
            schemata='Shop',
            widget=atapi.CalendarWidget(
                label=_(u'label_buyable_effective_date',
                        default=u'Buyable effective date'),
            ),
        ),
        XSharedBuyablePeriodDateTimeField(
            name='buyable_expires',
            schemata='Shop',
            widget=atapi.CalendarWidget(
                label=_(u'label_buyable_expiration_date',
                        default=u'Buyable expiration date'),
            ),
        ),
    ]


@implementer(IBuyablePeriod)
class ATSharedBuyablePeriod(object):
    # TODO: not used at all?

    def __init__(self, context):
        self.context = context

    @property
    def effective(self):
        shared_data = ISharedBuyablePeriodData(self.context)
        effective = shared_data.get('buyable_effective')
        if effective:
            effective = datetime.fromtimestamp(effective)
        return effective

    @property
    def expires(self):
        shared_data = ISharedBuyablePeriodData(self.context)
        expires = shared_data.get('buyable_expires')
        if expires:
            expires = datetime.fromtimestamp(expires)
        return expires
