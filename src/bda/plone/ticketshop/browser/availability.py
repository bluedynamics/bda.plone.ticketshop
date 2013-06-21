from zope.component import adapter
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.cart import (
    extractitems,
    readcookie,
)
from bda.plone.shop.browser.availability import CartItemAvailability
from ..interfaces import (
    ISharedStock,
    ISharedStockData,
)


@adapter(ISharedStock, IBrowserRequest)
class SharedCartItemAvailability(CartItemAvailability):
    details_template = ViewPageTemplateFile('availability_details.pt')

    @property
    def available(self):
        available = self.stock.available
        shared_stock_data = ISharedStockData(self.context)
        related_uids = shared_stock_data.related_uids
        if available is not None:
            cart_items = extractitems(readcookie(self.request))
            for item_uid in related_uids:
                for uid, count, comment in cart_items:
                    if uid == item_uid:
                        available -= float(count)
        return available
