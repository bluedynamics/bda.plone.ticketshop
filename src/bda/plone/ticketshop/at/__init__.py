from zope.interface import implementer
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IExtensionField
from Products.Archetypes.public import FloatField
from ..interfaces import ITicketShopExtensionLayer
from ..interfaces import ITicketOccurrence
from ..interfaces import ISharedStock
from ..interfaces import ISharedStockData


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

    def set(self, instance, value, **kwargs):
        # XXX: gets called twice per field, first time with correct value
        #      second time with None.
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
            return ISharedStockData(instance).get(self.getName())
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor(**kw):
            return ISharedStockData(instance).get(self.getName())
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            self.set(instance, value, **kw)
            #ISharedStockData(instance).set(self.getName(), value)
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


class XSharedStockFloatField(SharedStockExtensionField, FloatField):
    pass


@adapter(ISharedStock)
class SharedStockExtender(ExtenderBase):
    layer = ITicketShopExtensionLayer
    fields = [
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
