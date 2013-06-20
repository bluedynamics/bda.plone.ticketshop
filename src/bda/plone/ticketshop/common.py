from zope.interface import implementer
from zope.component import adapter
from Acquisition import aq_parent
from zope.annotation.interfaces import IAnnotations
from bda.plone.cart.interfaces import ICartItemDataProvider
from .interfaces import ITicketOccurrence


@implementer(ICartItemDataProvider)
@adapter(ITicketOccurrence)
def TicketOccurrenceCartItemDataProviderProxy(context):
    return ICartItemDataProvider(aq_parent(context))


#         annotations = IAnnotations(self)
#         attachments = annotations.get(config.ANNOTATION_KEY, None)
#         if attachments is None:
#             attachments = OOBTree()
#              annotations[config.ANNOTATION_KEY] = attachments
