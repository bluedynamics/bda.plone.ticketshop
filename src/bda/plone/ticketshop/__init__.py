from Products.CMFCore import utils
from Products.Archetypes import atapi
from bda.plone.ticketshop import config


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    from .at import buyableevent
    from .at import ticket
    from .at import ticketoccurrence
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)
    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.meta_type),
            content_types=(atype,),
            permission=config.ADD_PERMISSIONS[atype.meta_type],
            extra_constructors=(constructor,),
            ).initialize(context)
