from bda.plone.shop.dx import default_item_cart_count_limit
from bda.plone.ticketshop import messageFactory as _
from bda.plone.ticketshop.dx.interfaces import IDXBuyableEvent
from bda.plone.ticketshop.interfaces import IBuyableEventData
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IBuyableEventBehavior(model.Schema, IDXBuyableEvent):

    model.fieldset(
        'shop',
        label=u"Shop",
        fields=[
            'item_cart_count_limit',
        ]
    )

    item_cart_count_limit = schema.Float(
        title=_(u'label_item_cart_count_limit',
                default=u'Max count of this item in cart'),
        required=False,
        defaultFactory=default_item_cart_count_limit
    )


@adapter(IDXBuyableEvent)
@implementer(IBuyableEventData)
class BuyableEventDataProvider(object):
    """Accessor Interface
    """

    def __init__(self, context):
        self.context = context

    @property
    def cart_count_limit(self):
        return self.context.item_cart_count_limit
