from zope.interface import implementer
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from archetypes.schemaextender.interfaces import (
    IExtensionField,
    IOrderableSchemaExtender,
    IBrowserLayerAwareExtender,
)
from Products.Archetypes.public import FloatField
from bda.plone.shop.interfaces import IShopExtensionLayer
from ..interfaces import ISharedStock


_ = MessageFactory('bda.plone.shop')


@implementer(IExtensionField)
class SharedStockExtensionField(object):

    def getAccessor(self, instance):
        def accessor(**kw):
            # XXX: from parent, by uid, start end
            return 99
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor(**kw):
            # XXX: from parent, by uid, start end
            return 99
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            print 'mutate'
            print value
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


class XFloatField(SharedStockExtensionField, FloatField): pass


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
@adapter(ISharedStock)
class SharedStockExtender(object):
    layer = IShopExtensionLayer

    fields = [
        XFloatField(
            name='item_available',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_item_available', u'Item stock available'),
            ),
        ),
        XFloatField(
            name='item_overbook',
            schemata='Shop',
            widget=FloatField._properties['widget'](
                label=_(u'label_item_overbook', u'Item stock overbook'),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        return original
