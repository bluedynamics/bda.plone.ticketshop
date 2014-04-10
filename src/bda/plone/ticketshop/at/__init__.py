from zope.interface import implementer
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IExtensionField
from Products.Archetypes.public import FloatField
from Products.Archetypes.public import BooleanField
from Products.Archetypes.interfaces import IFieldDefaultProvider
from bda.plone.shop.at import ATCartItemDataProvider
from ..interfaces import ITicketShopExtensionLayer
from ..interfaces import ITicketOccurrence
from ..interfaces import ISharedStock
from ..interfaces import ISharedStockData
from ..common import TicketShopCartDataProviderBase


_ = MessageFactory('bda.plone.shop')


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class ExtenderBase(object):

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        return original


@adapter(ITicketOccurrence)
class TicketOccurenceBuyableExtender(ExtenderBase):
    """Overwrite default buyable extender for ticket occurrences providing no
    fields.
    """
    layer = ITicketShopExtensionLayer
    fields = []


@implementer(IExtensionField)
class SharedStockExtensionField(object):

    def get(self, instance, **kwargs):
        __traceback_info__ = (self.getName(), instance, kwargs)
        return ISharedStockData(instance).get(self.getName())

    def getRaw(self, instance, **kwargs):
        return self.get(instance, **kwargs)

    def set(self, instance, value, **kwargs):
        if value == '':
            value = None
        elif value is not None:
            __traceback_info__ = (self.getName(), instance, value, kwargs)
            if isinstance(value, basestring):
                value = value.replace(',', '.')
            value = float(value)
        ISharedStockData(instance).set(self.getName(), value)

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


class XSharedStockFloatField(SharedStockExtensionField, FloatField): pass
class XSharedStockBooleanField(SharedStockExtensionField, BooleanField): pass


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
    ]


#@adapter(IBuyableEvent)
#@adapter(ITicket)
#@adapter(ITicketOccurrence)
class ATTicketShopCartDataProvider(TicketShopCartDataProviderBase,
                                   ATCartItemDataProvider):
    """XXX
    """
